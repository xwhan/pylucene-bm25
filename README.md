# Test the default pylucene bm25 for open-domain QA (Natural Questions)

Only tested for java-8-openjdk-amd64 

In bash 

export CLASSPATH=$CLASSPATH:data/corenlp/*:~/lucene/lucene-8.7.0/core/lucene-core-8.7.0.jar:~/lucene/lucene-8.7.0/queryparser/lucene-queryparser-8.7.0.jar:~/lucene/lucene-8.7.0/analysis/common/lucene-analyzers-common-8.7.0.jar:~/lucene/lucene-8.7.0/demo/lucene-demo-8.7.0.jar

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64


## Construct the corpus index

```
python indexer.py --corpus-path /data/xwhan/data/nq-dpr/corpus/psgs_w100.tsv --index-path /home/xwhan/data/nq-dpr/corpus/lucene_index 
```

## testing the retrieval

```
python retriever.py 
```

Answer Recall
| Method | Top20 | Top 50 | Top 100 |
| ------- | ------ | -------- | ------- |
| pylucene | 61.9 | 71.0 | 76.5 |
| [DPR](https://arxiv.org/pdf/2004.04906.pdf) | 78.4 | - | 85.4 |

