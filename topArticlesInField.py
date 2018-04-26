from Bio import Entrez,Medline
from copy import copy
from progress.bar import Bar
import argparse
Entrez.email = "example@mail.org"

class TopArticlesExtractor():

	def __init__(self, startId, topn=5, depth=5):
		self.startId = startId
		self.connectedIds = {}
		self.visited = set()
		self.toDo = set([self.startId])

		self.returnTop(topn=topn, depth=depth)

	def addId(self, i, l):
		"""
		add edge in our connected ids from i to l
		ignore this if already l to i in it
		"""
		if not i in self.connectedIds:
			self.connectedIds[i] = set()
		if l in self.connectedIds:
			if i in self.connectedIds[l]:
				return
		self.connectedIds[i].add(l)
	
	def returnTop(self, topn, depth):
		"""
		main function for searching the most interesting articles
		"""
		bar = Bar("Search Articles", max = depth)
		for _ in range(depth):
			new = set()
			handle = Entrez.elink(dbfrom="pubmed", id=self.toDo, linkname="pubmed_pubmed")
			records = Entrez.read(handle)
			handle.close()
			for record in records:
				linked = [link["Id"] for link in record["LinkSetDb"][0]["Link"]][:10]
				for l in linked[1:]:
					self.addId(l,linked[0])
					if l not in self.visited:
						new.add(l)
			self.toDo = copy(new)
			bar.next()
		bar.finish()

		print("Sort Articles")
		sortByIncEdges = [x[0] for x in sorted(self.connectedIds.items(), key = lambda x:len(x[1]), reverse=True)[:20]]

		handle = Entrez.efetch(db="pubmed", id=sortByIncEdges, rettype="medline", retmode="text")
		results = list(Medline.parse(handle))

		print("\n".join([i["PMID"] + " - " + i["TI"] for i in results]))

	def conToCSV(self, folder):
		"""
		convert connections to csv node and edges file for gephi graph explorer for further visualisation
		"""
		if not folder[-1] == "/":
			folder += "/"

	    nodes = connectedIds.keys()
	    with open(folder + "nodes.csv", "w") as f:
	        f.write("Id\n")
	        for node in nodes:
	            f.write(node+"\n")
	    
	    with open(folder + "edges.csv", "w") as f:
	        f.write("Source,Target\n")
	        for n in nodes:
	            for m in connectedIds[n]:
	                f.write("{},{}\n".format(n,m))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("id", help="sets starting pubmed id", type=int)
	args = parser.parse_args()

	ta = TopArticlesExtractor(args.id)