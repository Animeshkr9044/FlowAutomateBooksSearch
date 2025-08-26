from typing import Dict, Optional, List
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range, SearchParams

class QdrantSearcher:
    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def build_qdrant_filter(self, filter_dict: Dict) -> Optional[Filter]:
        """Convert filter dictionary to Qdrant Filter object"""
        try:
            if not filter_dict.get("must"):
                return None
            
            conditions = []
            for condition in filter_dict["must"]:
                key = condition["key"]
                
                if "match" in condition:
                    match_condition = condition["match"]
                    if "value" in match_condition:
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=match_condition["value"]))
                        )
                    elif "any" in match_condition:
                        for value in match_condition["any"]:
                            conditions.append(
                                FieldCondition(key=key, match=MatchValue(value=value))
                            )
                
                elif "range" in condition:
                    range_condition = condition["range"]
                    conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(
                                gte=range_condition.get("gte"),
                                lte=range_condition.get("lte"),
                                gt=range_condition.get("gt"),
                                lt=range_condition.get("lt")
                            )
                        )
                    )
            
            return Filter(must=conditions) if conditions else None
        except Exception as e:
            print(f"Error building Qdrant filter: {e}")
            return None

    def scroll_all(self, limit: int = 1000) -> List:
        """Scroll through all documents in the collection"""
        all_points = []
        next_offset = None
        
        while True:
            try:
                results, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=limit,
                    offset=next_offset,
                    with_payload=True
                )
                all_points.extend(results)
                if next_offset is None:
                    break
            except Exception as e:
                print(f"Error during Qdrant scroll: {e}")
                break
                
        return all_points

    def search(self, query_embedding: List[float], qdrant_filter: Optional[Filter], limit: int) -> List:
        """Perform a search in Qdrant"""
        try:
            return self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                query_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                search_params=SearchParams(hnsw_ef=128, exact=False)
            )
        except Exception as e:
            print(f"Error during Qdrant search: {e}")
            return []
