#!/usr/bin/env python

# Name: wordsworth
# Description: Frequency analysis tool
# Author: autonomoid
# Date: 2014-06-22
# Licence: GPLv3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import re
import collections
import nltk
import json

# Font effects --> fancy console colours in bash
underline = "\x1b[1;4m"
black = "\x1b[1;30m"
red = "\x1b[1;31m"
green = "\x1b[1;32m"
yellow = "\x1b[1;33m"
blue = "\x1b[1;34m"
purple = "\x1b[1;35m"
turquoise = "\x1b[1;36m"
normal = "\x1b[0m"

previous_word = ''
previous_pair = ''
previous_triple = ''
previous_quad = ''


def print_n_word_frequencies(n_word_counter, top_n, out, tag=None):
    total_entries = sum(n_word_counter.values())
    unique_entries = len(n_word_counter)
    if total_entries > 0:
        m = n_word_counter.most_common(min(unique_entries, top_n))
        n = len(m[0][0].split(' '))

        if tag == None:
            print '\n===' + blue + ' Commonest ' + str(n) + '-words' + normal + ' ==='
            out.write('\n=== Commonest ' + str(n) + '-words ===\n')
        else:
            print '\n===' + blue + ' Commonest ' + tag + normal + ' ==='
            out.write('\n=== Commonest ' + tag + ' ===\n')

        for i in range(0, min(unique_entries, top_n)):
            n_word = m[i][0]
            count = m[i][1]
            perc = 100.0 * (count / float(total_entries))

            print (str(i + 1) + ' = ' + purple + n_word +
                   normal + ' (' + purple + str(count).split('.')[0] + normal +
                   ' = ' + purple + str(perc)[:5] + '%' + normal + ')')

            out.write(str(i + 1) + ' = ' + n_word + ' (' + str(count).split('.')[0] +
            ' = ' + str(perc)[:5] + '%)\n')



# PERFORM NLP ANALYSIS
#   input = text file to parse
#   max_n_word = the max length n-gram. default is 4
#   top_n = the top n most frequent k-grams. default is 20
#   allowdigits = allow digits to be parsed. default is true
#   ignore_list = file of words to ignore
def nlp_analyze(input_list, max_n_word=4, top_n=20, allow_digits=True):
   
    # build ignore list from argument file
    with open('ignore2.json') as ignore_json:
        ignore_list = json.load(ignore_json);

    # Dynamically allocated n-word counters
    n_words = ['' for i in range(max_n_word)]
    prev_n_words = ['' for i in range(max_n_word)]
    counters = [collections.Counter() for i in range(max_n_word)]

    # Read in all of the words in a file
    print "[nlp] Reading reviews..."
    text = '. '.join(input_list).lower()
    print "[debuggery] joined text: " + text

    # Use nltk to classify/tag each word/token.
    print "[nlp] Tokenizing text..."
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')
    tokens = tokenizer.tokenize(text)

    print "[nlp] Tagging tokens..."
    tagger = nltk.UnigramTagger(nltk.corpus.brown.tagged_sents())
    tagged_tokens = tagger.tag(tokens)

    print "[nlp] Tallying tags..."
    personal_pronoun_counter = collections.Counter()
    adjective_counter = collections.Counter()
    adverb_counter = collections.Counter()
    noun_counter = collections.Counter()
    verb_counter = collections.Counter()

    for token in tagged_tokens:

        if token[1] == None:
            continue

        elif 'PPS' in token[1]:
            personal_pronoun_counter[token[0]] += 1

        elif 'JJ' in token[1]:
            adjective_counter[token[0]] += 1

        elif 'NN' in token[1]:
            noun_counter[token[0]] += 1

        elif 'RB' in token[1]:
            adverb_counter[token[0]] += 1

        elif 'VB' in token[1]:
            verb_counter[token[0]] += 1

     # Shall we include digits?
    if allow_digits:
        words = re.findall(r"['\-\w]+", text)
    else:
        words = re.findall(r"['\-A-Za-z]+", text)

    print "[nlp] Performing frequency analysis of n-words..."
    for word in words:
    
        word = word.strip(r"&^%$#@!")       

        if word in ignore_list:
            continue

        # Allow hyphenated words, but not hyphens as words on their own.
        if word == '-':
            continue

        # Tally words.
        for i in range(1, max_n_word):
            if prev_n_words[i - 1] != '':
                n_words[i] = prev_n_words[i - 1] + ' ' + word
                counters[i][n_words[i]] += 1

        n_words[0] = word
        counters[0][word] += 1

        for i in range(0, max_n_word):
            prev_n_words[i] = n_words[i]


    # Print results
    out = open('output-stats.txt', 'w')

    print '\n===' + blue + ' RESULTS ' + normal + '==='
    out.write('=== RESULTS ===\n')

    for i in range(max_n_word):
        print_n_word_frequencies(counters[i], top_n, out)

    print_n_word_frequencies(personal_pronoun_counter, top_n, out, tag="Personal Pronouns")
    print_n_word_frequencies(noun_counter, top_n, out, tag="Nouns")
    print_n_word_frequencies(adjective_counter, top_n, out, tag="Adjectives")
    print_n_word_frequencies(adverb_counter, top_n, out, tag="Adverbs")
    print_n_word_frequencies(verb_counter, top_n, out, tag="Verbs")

    out.close()


