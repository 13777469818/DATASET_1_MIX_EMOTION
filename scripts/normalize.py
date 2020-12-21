import argparse
import databaker


def write_metadata(metadata, out_path):
  with open(out_path, 'w', encoding='utf-8-sig') as f:
    for m in metadata:
      f.write('|'.join([str(x) for x in m]) + '\n')
  print('Write {} utterances.'.format(len(metadata)))


def main():
  print('Doing normalizing..')
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', default='main.txt')
  parser.add_argument('--output', default='metadata.csv')
  parser.add_argument('--prosody', type=bool, default=True)
  parser.add_argument('--english', type=bool, default=False)
  args = parser.parse_args()

  if args.english==True:
    metadata = databaker.parse_labels_en(args.input)
  else:
    metadata = databaker.parse_labels_cn(args.input, args.prosody)

  write_metadata(metadata, args.output)


if __name__ == '__main__':
	main()
