import xml.etree.ElementTree as ET
import bisect
import datetime

class OrderBook:
 
    def __init__(self):
        self.order_books = {}
        self.orderIdMap = {}

    def addBook(self, book):

        if book not in self.order_books.keys():
            self.order_books[book] =  {}
            self.order_books[book]["BUY"] = []
            self.order_books[book]["SELL"] = []
    
    def addSellOrder(self, book, order_detail):

        while len(self.order_books[book]["BUY"]) > 0 and self.order_books[book]["BUY"][0][0] >= order_detail[0]:
            if self.order_books[book]["BUY"][0][1] <= order_detail[1]:
                order_detail[1] -= self.order_books[book]["BUY"][0][1]
                self.order_books[book]["BUY"].pop(0)
                if order_detail[0] == 0:
                    return 
            else:
                self.order_books[book]["BUY"][0][1] -= order_detail[1]  
                return 
          
        bisect.insort(self.order_books[book]["SELL"], order_detail, key=lambda x: x[0])

    def addBuyOrder(self, book, order_detail):
       
        while len(self.order_books[book]["SELL"]) > 0 and self.order_books[book]["SELL"][0][0] <= order_detail[0]:
            if self.order_books[book]["SELL"][0][1] <= order_detail[1]:
                order_detail[1] -= self.order_books[book]["SELL"][0][1]
                self.order_books[book]["SELL"].pop(0)
                if order_detail[0] == 0:
                    return 
            else:
                self.order_books[book]["SELL"][0][1]-= order_detail[1]  
                return 
        bisect.insort(self.order_books[book]["BUY"], order_detail, key=lambda x: -1 * x[0])

    def deleteOrder(self, book, orderId):
        if book != self.orderIdMap[orderId][0]:
            return 
        
        operation = self.orderIdMap[orderId][1]
        for i in range(len(self.order_books[book][operation])):
            if self.order_books[book][operation][i][2] ==  orderId:
                self.order_books[book][operation].pop(i)
                return 
         
    def printOutput(self):

        for book in sorted(self.order_books.keys()):
            print(f"\nbook: {book}")
            print("Buy".rjust(15) + " -- " + "Sell")
            print("=" * 35)

            buy_orders = self.order_books[book]['BUY']
            sell_orders = self.order_books[book]['SELL']
            max_orders = max(len(buy_orders), len(sell_orders))

            for i in range(max_orders):
                buy_str = (f"{buy_orders[i][1]}@{buy_orders[i][0]:.2f}" if i < len(buy_orders) else "").rjust(15)
                sell_str = (f"{sell_orders[i][1]}@{sell_orders[i][0]:.2f}" if i < len(sell_orders) else "")
                print(f"{buy_str} -- {sell_str}")
                        
    def ReadOrderData(self, order_file_path):

        start_datetime = datetime.datetime.now()
        formatted_datetime = start_datetime.strftime("Processing started at: %Y-%m-%d %H:%M:%S.%f")
        print(formatted_datetime)

        with open(order_file_path, 'r') as f:
            order_data = f.read().split("\n")

        for order in order_data:
            try:
                root = ET.fromstring(order)
                tag = root.tag
            except:
                continue
            if tag == "AddOrder":

                book = root.get('book')
                operation = root.get('operation')
                order_detail = [float(root.get('price')), int(root.get('volume')), int(root.get('orderId'))]
                self.orderIdMap[order_detail[2]] = [book, operation, order_detail[0:2]]
                if book not in self.order_books.keys():
                    self.addBook(book)

                if operation == "SELL":
                    self.addSellOrder(book, order_detail)
                else:
                    self.addBuyOrder(book, order_detail)

            else:
                book = root.get('book')
                orderId = int(root.get('orderId'))
                self.deleteOrder(book, orderId)
        
        self.printOutput()

        completed_datetime = datetime.datetime.now()
        formatted_datetime = completed_datetime.strftime("\nProcessing completed at: %Y-%m-%d %H:%M:%S.%f")
        print(formatted_datetime)

        total_time = (completed_datetime - start_datetime).seconds
        print(f"Processing Duration: {total_time} seconds")

orderbook = OrderBook()
orderbook.ReadOrderData("orders 1.xml")