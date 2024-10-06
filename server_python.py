import http.server
import socketserver
from urllib.parse import parse_qs
from auth_service import UserService
from item_service import ItemService

PORT = 3001
DB_NAME = 'login_system.db'

class MyHandler(http.server.SimpleHTTPRequestHandler):
    
    item_service = ItemService(DB_NAME)    
    user_service = UserService(DB_NAME)
    
    def do_GET(self):
        if self.path == "/":  # Formulario de login
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_content = b"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login</title>
            </head>
            <body>
                <form action="/login" method="POST">
                    <h2>Login</h2>
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                    <br>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                    <br>
                    <button type="submit">Login</button>
                    <button type="submit" formaction="/register">Register</button>
                </form>
            </body>
            </html>
            """
            self.wfile.write(html_content)
        elif self.path == "/search":  # Formulario de búsqueda de ítems
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_content = b"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Search Item</title>
            </head>
            
            <body>
                <h2>Search Items</h2>
                <form action="/search_item" method="POST">
                    <label for="search_query">Search by Name or ID:</label>
                    <input type="text" id="search_query" name="search_query" required>
                    <button type="submit">Search</button>
                </form>
                <h2>Add New Item</h2>
                <form action="/add_item" method="POST">
                    <label for="item_name">Item Name:</label>
                    <input type="text" id="item_name" name="item_name" required>
                    <br>
                    <label for="item_description">Item Description:</label>
                    <input type="text" id="item_description" name="item_description" required>
                    <br>
                    <button type="submit">Add Item</button>
                    </form>
                
                <br>
                <form action="/logout" method="POST">
                    <button type="submit">Logout</button>
                </form>
            </body>
            </html>
            """
            self.wfile.write(html_content)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = parse_qs(post_data.decode('utf-8'))
        
        if self.path == "/logout":
            # Redirigir al formulario de login al hacer logout            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>You have been logged out.</h2><a href='/'>Login Again</a>")
            return
        
        if self.path == "/add_item":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = parse_qs(post_data.decode('utf-8'))
            
            item_name = params.get('item_name')[0]
            item_description = params.get('item_description')[0]

            if item_name and item_description:
                self.item_service.add_item(item_name, item_description)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h2>Item added successfully!</h2><a href='/search'>Go back</a>")
            else:
                self.send_error(400, "Missing item name or description")
            return
        if self.path == "/search_item": 
                             
            search_query = params.get('search_query', [None])[0]
            print(f"Search query received: {search_query}")
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
                           
            if search_query:  
                items = self.item_service.get_item_by_name_or_id(search_query)
            else:
                items = None

            if items and len(items) > 0:
                print ("entró por acá")
                self.wfile.write(b"<h2>Items Found:</h2>")
                self.wfile.write(b"<ul>")
                for item in items:
                    item_html = f"<li>ID: {item[0]}, Name: {item[1]}, Description: {item[2]}</li>"
                    self.wfile.write(item_html.encode('utf-8'))
                self.wfile.write(b"</ul>")
                self.wfile.write(b"<a href='/search'>Go back</a>")
            else:
                self.wfile.write(b"<h2>No items found</h2><a href='/search'>Go back</a>")
            return    
        
        username = params.get('username')
        password = params.get('password')
        
        username = username[0]
        password = password[0]
        
        if not username or not password:
            self.send_error(400, "Missing username or password")
            return
        
        if self.path == "/login":
                    
            if self.user_service.user_exists(username):
                if self.user_service.authenticate_user(username, password):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h2>Login Successful</h2><br><br><a href='/search'>Search Items</a>")
                else:
                    self.send_error(403, "Invalid credentials")
            else:
                self.send_error(403, "User does not exist")
        
        elif self.path == "/register":
            
            if not self.user_service.user_exists(username):
                self.user_service.create_user(username, password)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h2>User created successfully</h2><a href='/search'>Search Items</a>")
            else:
                self.send_error(400, "User already exists")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()
