'''
Script that queries the logging endpoint for solr /select queries, parses the results and optionally saves them in a file
'''

import json
import requests
import argparse
import sys,os

def main():

  parser = argparse.ArgumentParser()

  parser.add_argument(
    '--date-glob-string',
    nargs=1,
    default=u'2014.*.*',
    dest='dateGlobString',
    help='Logging glob pattern',
  )

  parser.add_argument(
    '--N_results',
    nargs=1,
    default=u'10000',
    dest='size',
    help='How many results to get from logging',
  )

  parser.add_argument(
    '--HTTPendpoint',
    nargs=1,
    default=u'http://localhost:9200/logstash-%(date)s/solr-logs/_search?size=%(size)s&fields=param__q,params&q=path.raw:"/select"',
    dest='HTTPendpoint',
    help='HTTP endpoint for logging, with python string interpolation around date and size',
  )

  parser.add_argument(
    '--solr-url',
    nargs=1,
    default=u'http://localhost:8983/solr/select?%(query)s',
    dest='solr_url',
    help='solr_url, with python string inperolation around query',
  )

  parser.add_argument(
    '--excluded-queries',
    nargs='*',
    default=[u'wt=json&q=star'],
    dest='excluded_queries',
    help='Queries to exclude',
  )

  parser.add_argument(
    '--output',
    nargs=1,
    default=sys.stdout,
    dest='output',
    help='Filename to write results to. Default to sys.stdout',
  )

  args = parser.parse_args()

  r = requests.get(args.HTTPendpoint % {'date': args.dateGlobString, 'size': args.size } )

  URLs = []
  for record in r.json()['hits']['hits']:
    q = record['fields']['params'][0]
    if q in args.excluded_queries:
      continue
    URLs.append(
       args.solr_url % {'query': q} 
    )

  try:
    print >> args.output, '\n'.join(URLs)
  except AttributeError:
    with open(args.output[0],'w') as fp:
      print >> fp, '\n'.join([u.encode('utf-8') for u in URLs])


if __name__ == '__main__':
  main()
