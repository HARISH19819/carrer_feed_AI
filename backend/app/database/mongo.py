import copy
import re
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.core.logging import logger

class InMemoryCursor:
    def __init__(self, items):
        self._items = list(items)

    def sort(self, key_or_list, direction=None):
        if isinstance(key_or_list, list):
            for k, d in reversed(key_or_list):
                reverse = (d == -1)
                self._items.sort(key=lambda x: (x.get(k) is None, x.get(k)), reverse=reverse)
        elif isinstance(key_or_list, str):
            reverse = (direction == -1)
            self._items.sort(key=lambda x: (x.get(key_or_list) is None, x.get(key_or_list)), reverse=reverse)
        return self

    def skip(self, n):
        self._items = self._items[n:]
        return self

    def limit(self, n):
        self._items = self._items[:n]
        return self

    async def to_list(self, length=None):
        if length is not None:
            return copy.deepcopy(self._items[:length])
        return copy.deepcopy(self._items)

    def __aiter__(self):
        self._iter = iter(copy.deepcopy(self._items))
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration

class InMemoryCollection:
    def __init__(self, name):
        self.name = name
        self._docs = []

    def _match_doc(self, doc, query):
        if not query:
            return True
        for k, v in query.items():
            if k == "$or":
                sub_matches = [self._match_doc(doc, sub_q) for sub_q in v]
                if not any(sub_matches):
                    return False
                continue
            doc_val = doc.get(k)
            # Handle ObjectId vs str matching for IDs
            if k == "_id" or k.endswith("_id") or k == "id":
                if str(doc_val) != str(v):
                    return False
                continue
            if isinstance(v, dict):
                if "$regex" in v:
                    pattern = v["$regex"]
                    flags = re.IGNORECASE if v.get("$options") == "i" else 0
                    if doc_val is None:
                        return False
                    if isinstance(doc_val, list):
                        if not any(re.search(pattern, str(item), flags) for item in doc_val):
                            return False
                    elif not re.search(pattern, str(doc_val), flags):
                        return False
                elif "$in" in v:
                    if doc_val not in v["$in"]:
                        return False
            else:
                if doc_val != v:
                    return False
        return True

    async def find_one(self, query=None, *args, **kwargs):
        query = query or {}
        for doc in self._docs:
            if self._match_doc(doc, query):
                return copy.deepcopy(doc)
        return None

    def find(self, query=None, *args, **kwargs):
        query = query or {}
        matched = [doc for doc in self._docs if self._match_doc(doc, query)]
        return InMemoryCursor(matched)

    async def count_documents(self, query=None, *args, **kwargs):
        query = query or {}
        matched = [doc for doc in self._docs if self._match_doc(doc, query)]
        return len(matched)

    async def insert_one(self, document):
        doc = copy.deepcopy(document)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self._docs.append(doc)
        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertOneResult(doc["_id"])

    async def insert_many(self, documents):
        inserted_ids = []
        for d in documents:
            doc = copy.deepcopy(d)
            if "_id" not in doc:
                doc["_id"] = ObjectId()
            self._docs.append(doc)
            inserted_ids.append(doc["_id"])
        class InsertManyResult:
            def __init__(self, ids):
                self.inserted_ids = ids
        return InsertManyResult(inserted_ids)

    async def update_one(self, query, update, upsert=False):
        matched_doc = None
        for doc in self._docs:
            if self._match_doc(doc, query):
                matched_doc = doc
                break
        
        if matched_doc:
            if "$set" in update:
                for k, v in update["$set"].items():
                    matched_doc[k] = copy.deepcopy(v)
            class UpdateResult:
                matched_count = 1
                modified_count = 1
            return UpdateResult()
        elif upsert:
            new_doc = copy.deepcopy(query)
            if "$set" in update:
                new_doc.update(copy.deepcopy(update["$set"]))
            await self.insert_one(new_doc)
            class UpsertResult:
                matched_count = 0
                modified_count = 1
            return UpsertResult()
        
        class NoUpdateResult:
            matched_count = 0
            modified_count = 0
        return NoUpdateResult()

    async def delete_one(self, query):
        for i, doc in enumerate(self._docs):
            if self._match_doc(doc, query):
                del self._docs[i]
                class DeleteResult:
                    deleted_count = 1
                return DeleteResult()
        class NoDeleteResult:
            deleted_count = 0
        return NoDeleteResult()

    async def create_index(self, *args, **kwargs):
        return "in_memory_index"

class InMemoryDatabase:
    def __init__(self):
        self._collections = {}

    def __getattr__(self, name):
        if name not in self._collections:
            self._collections[name] = InMemoryCollection(name)
        return self._collections[name]

    def __getitem__(self, name):
        return getattr(self, name)

# Global singleton in-memory database fallback
in_memory_db = InMemoryDatabase()

class DatabaseManager:
    client: AsyncIOMotorClient = None
    db = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=2000
        )
        # Ping server to confirm connection
        await client.admin.command('ping')
        db_manager.client = client
        db_manager.db = client[settings.DATABASE_NAME]
        logger.info(f"Successfully connected to MongoDB database: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.warning(f"MongoDB connection to {settings.MONGODB_URI} failed: {e}. Activating resilient In-Memory Database.")
        db_manager.client = None
        db_manager.db = in_memory_db

async def close_mongo_connection():
    if db_manager.client is not None:
        logger.info("Closing MongoDB connection...")
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_manager.db if db_manager.db is not None else in_memory_db
