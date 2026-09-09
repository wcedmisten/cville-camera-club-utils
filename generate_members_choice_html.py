import argparse


parser = argparse.ArgumentParser(
                    prog='CCC File Parser',
                    description='Parses CCC photo files',
                    epilog='Made by William Edmisten')

parser.add_argument('file_prefix', help='The file prefix, e.g. Slide')
parser.add_argument('file_suffix', help='The file suffix, e.g. .JPG')
parser.add_argument('num_files', type=int, help='The number of files to generate HTML for')

args = parser.parse_args()

for i in range(0, args.num_files):
    print(f"""<p><img src="/sites/default/files/{args.file_prefix}{i}{args.file_suffix}" alt="" width="1024" height="768" /></p>""")