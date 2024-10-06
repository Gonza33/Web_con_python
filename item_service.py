from db_connection import DatabaseConnection

class ItemService:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_item_by_name_or_id(self, search_query):
        query = """
        SELECT id, item_name, item_description 
        FROM items 
        WHERE id = ? OR item_name LIKE ?"""
        with DatabaseConnection(self.db_name) as db:
            try:
                search_id= int(search_query)
            except ValueError:
                search_id= None
            db.execute(query, (search_id, f"%{search_query}%"))
            result=db.fetchall()
        return result

    def add_item(self, item_name, item_description):
        query = "INSERT INTO items (item_name, item_description) VALUES (?, ?)"
        with DatabaseConnection(self.db_name) as db:
            db.execute(query, (item_name, item_description))