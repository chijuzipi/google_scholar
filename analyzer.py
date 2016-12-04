from pymongo import MongoClient

class Analyzer:
  def __init__(self, database):
    client = MongoClient()
    self.db = client[database]
    self.totalCite = 0
    col1, col2 = self.getCollections()
    self.analyze(col1, col2)
    print self.totalCite

  def getCollections(self):
    collections = self.db.collection_names()
    collections.remove('system.indexes')
    list.sort(collections)
    print collections
    l = len(collections)
    return self.db[collections[l-2]], self.db[collections[l-1]]

  def analyze(self, col1, col2):
    cursor1 = col1.find()  
    for record1 in cursor1:
      title = record1['title'] 
      cursor2 = col2.find()
      for record2 in cursor2:
        if record2['title'] == title:
          self.compareRecord(record1, record2, title)

    print 'total cite', self.totalCite

  
  def compareRecord(self, rec1, rec2, title):
    print 
    print title
    self.totalCite += rec2['citation']

    if rec1['citation'] == rec2['citation']:
      print '-- No Change --' + str(rec1['citation']) + '--'
      return
    elif rec1['citation'] > rec2['citation']:
      out = self.compare(rec1, rec2)
      print '-- Bad News --' + 'minus : ' + str(rec1['citation'] - rec2['citation'])
      for item in out:
        print item
    else:
      out = self.compare(rec2, rec1)
      print '-- Good News!! --' + 'add : ' + str(rec2['citation'] - rec1['citation'])
      for item in out:
        print item

  def compare(self, rec1, rec2):
    bag = set()     
    out = []
    for item in rec2['citeTitle']:
      bag.add(item)
    for item in rec1['citeTitle']:
      if item not in bag:
        out.append(item)
    return out
    
def main():
  analyzer = Analyzer('yuzhou')

if __name__ == '__main__':
  main()

