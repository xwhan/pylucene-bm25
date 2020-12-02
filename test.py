import lucene
from java.io import StringReader
from org.apache.lucene.analysis.ja import JapaneseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
# Basic tokenizer example.
test = "This is how we do it."
tokenizer = StandardTokenizer()
tokenizer.setReader(StringReader(test))
charTermAttrib = tokenizer.getAttribute(CharTermAttribute.class_)
tokenizer.reset()
tokens = []
while tokenizer.incrementToken():
    tokens.append(charTermAttrib.toString())
print(tokens)
# StandardAnalyzer example.
analyzer = StandardAnalyzer()
stream = analyzer.tokenStream("", StringReader(test))
stream.reset()
tokens = []
while stream.incrementToken():
    tokens.append(stream.getAttribute(CharTermAttribute.class_).toString())
print(tokens)
# JapaneseAnalyzer example.
analyzer = JapaneseAnalyzer()
test = "寿司が食べたい。"
stream = analyzer.tokenStream("", StringReader(test))
stream.reset()
tokens = []
while stream.incrementToken():
    tokens.append(stream.getAttribute(CharTermAttribute.class_).toString())
print(tokens)
