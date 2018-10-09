#!/usr/bin/python
# -*- coding: utf-8 -*-

from py2neo import Graph
from igraph import Graph as IGraph

#链接到NEO4J
graph = Graph(
	"http://localhost:7474",
	username = "neo4j",
	password = "651219"
)

#创建一个IGraph类
query = ''' MATCH (c1:Character)-[r:INTERACTS]->(c2:Character) RETURN c1.name, c2.name, r.weight AS weight '''
ig = IGraph.TupleList(graph.run(query), weights=True)

'''网页排名'''
pg = ig.pagerank()
pgvs = []
for (p,pg) in zip(ig.vs, pg):
	# print(p, pg)
	pg = str(pg)
	pgvs.append({"name": p["name"], "pg": pg})

write_clusters_query = ''' UNWIND {nodes} AS n MATCH (c:Character) WHERE c.name = n.name SET c.pagerank = n.pg '''
graph.run(write_clusters_query, nodes=pgvs)

'''
在neo4j中运行
MATCH (n:Character) RETURN n.name AS name, n.pagerank AS pagerank ORDER BY pagerank DESC LIMIT 10
'''


'''最小社区'''
clusters = IGraph.community_walktrap(ig, weights="weight").as_clustering()
nodes = [{"name": node["name"]} for node in ig.vs]
for node in nodes:
	idx = ig.vs.find(name=node["name"]).index
	node["community"] = clusters.membership[idx]

write_clusters_query = ''' UNWIND {nodes} AS n MATCH (c:Character) WHERE c.name = n.name SET c.community = toInt(n.community) '''
graph.run(write_clusters_query, nodes=nodes)

'''
在neo4j运行
MATCH (c:Character) WITH c.community AS cluster, collect(c.name) AS  members RETURN cluster, members ORDER BY cluster ASC    
'''

