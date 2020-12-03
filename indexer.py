#!/usr/bin/env python

import sys, os, lucene, threading, time, csv, argparse
from datetime import datetime
from tqdm import tqdm

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import NIOFSDirectory


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class Indexer(object):

    def __init__(self, corpusPath, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = NIOFSDirectory(Paths.get(storeDir))
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(corpusPath, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs(self, corpusPath, writer):

        metaType = FieldType()
        metaType.setStored(True)
        metaType.setTokenized(False)
        # metaType.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        contextType = FieldType()
        contextType.setStored(True)
        contextType.setTokenized(True)
        contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        # adding corpus
        with open(corpusPath) as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            for row in tqdm(reader):
                if row[0] != 'id':
                    doc_id, text, title = row[:3]
                    doc = Document()
                    doc.add(Field('Title', title, metaType))
                    doc.add(Field('ID', str(doc_id), metaType))
                    doc.add(Field('Context', text, contextType))
                    writer.addDocument(doc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus-path', type=str, help='raw corpus path')
    parser.add_argument('--index-path', type=str, help='file index save path')
    args = parser.parse_args()

    if os.path.exists(args.index_path):
        print("Index already exists...")
    else:
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        start = datetime.now()
        try:
            corpusIndex = Indexer(args.corpus_path, args.index_path)
            end = datetime.now()
            print(end - start)
        except Exception as e:
            print("Failed: ", e)
            raise e
