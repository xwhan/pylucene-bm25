import json
import sys
import argparse
import lucene
import numpy as np
from multiprocessing import Pool as ProcessPool
from functools import partial
from collections import defaultdict
from tqdm import tqdm

from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher

# evaluation tools from MDR
from mdr.retrieval.utils.utils import para_has_answer
from mdr.retrieval.utils.basic_tokenizer import SimpleTokenizer

from multiprocessing import Pool as ProcessPool
from multiprocessing.util import Finalize

PROCESS_TOK = None
def init():
    global PROCESS_TOK
    PROCESS_TOK = SimpleTokenizer()
    Finalize(PROCESS_TOK, PROCESS_TOK.shutdown, exitpriority=100)


def get_score(answer_doc, topk=20):
    """Search through all the top docs to see if they have the answer."""
    question, answer, docs = answer_doc

    global PROCESS_TOK
    topkpara_covered = []
    for p in docs:
        topkpara_covered.append(int(para_has_answer(answer, p["title"] + " " + p["text"], PROCESS_TOK)))

    return {
        "5": int(np.sum(topkpara_covered[:5]) > 0),
        "10": int(np.sum(topkpara_covered[:10]) > 0),
        "20": int(np.sum(topkpara_covered[:20]) > 0),
        "50": int(np.sum(topkpara_covered[:50]) > 0),
        "100": int(np.sum(topkpara_covered[:100]) > 0),
        # "covered": topkpara_covered
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index-path', type=str, help='lucene index path', default='/home/xwhan/data/nq-dpr/corpus/lucene_index')
    parser.add_argument('--qa-data', type=str, help='qa data for evaluation', default='/home/xwhan/data/nq/nq-test.txt')
    parser.add_argument('--topk', type=int, default=100)
    args = parser.parse_args()

    qas = [json.loads(line) for line in open(args.qa_data).readlines()]
    questions = [_["question"][:-1] if _["question"].endswith("?") else
                 _["question"] for _ in qas]
    answers = [item["answer"] for item in qas]

    print("Loading Lucene Index ...")
    lucene.initVM(vmargs=['-Djava.aws.headless=true'])
    analyzer = StandardAnalyzer()
    searchDir = NIOFSDirectory(Paths.get(args.index_path))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))

    parser = QueryParser('Context', analyzer)
    

    retrieved = []
    print("Searching ...")
    for q in tqdm(questions):
        query = parser.parse(QueryParser.escape(q))
        scoreDocs = searcher.search(query, args.topk).scoreDocs
        topkDocs = []
        for hit in scoreDocs:
            doc = searcher.doc(hit.doc)
            topkDocs.append({
                "title": doc.get("Title"),
                "text": doc.get("Context")
            })
        retrieved.append(topkDocs)
    
    qas_docs = list(zip(questions, answers, retrieved))

    print("Evaluting answer recall ...")
    get_score_partial = partial(
        get_score, topk=args.topk)
    processes = ProcessPool(processes=20, initializer=init
    )
    results = processes.map(get_score_partial, qas_docs)

    aggregate = defaultdict(list)
    for r in results:
        for k, v in r.items():
            aggregate[k].append(v)

    for k in aggregate:
        results = aggregate[k]
        print('Top {:3d} Recall for {} QA pairs: {:.2f} ...'.format(
            int(k), len(results), np.mean(results)))
