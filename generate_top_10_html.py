# get the date_string from the current month and year
import argparse
from datetime import date

parser = argparse.ArgumentParser(
                    prog='CCC Top 10 HTML Generator',
                    description='Generates the top 10 HTML for the CCC website',
                    epilog='Made by William Edmisten')

parser.add_argument('scores_file', help='The zip file containing CCC files to parse')
args = parser.parse_args()

scores_file = args.scores_file

a_scores = []
b_scores = []

with open(scores_file, 'r') as f:
    lines = f.readlines()
    # get the header line to determine the index of the Class and Name and Total columns
    header = lines[0].strip().split(',')
    class_index = header.index('Class')
    name_index = header.index('Name')
    total_index = header.index('Total')

    print(f"Class index: {class_index}, Name index: {name_index}, Total index: {total_index}")

    for line in lines[2:]:
        splits = line.strip().split(',')
        print(line)
        member_class = splits[class_index]
        member_name = splits[name_index]
        member_total = int(splits[total_index])
        if member_class == 'A':
            a_scores.append({"member_name": member_name, "member_total": member_total})
        elif member_class == 'B':
            b_scores.append({"member_name": member_name, "member_total": member_total})

# get the top 10 scores for each class, or more if there are ties
def get_top_10(scores):
    scores = sorted(scores, key=lambda x: x['member_total'], reverse=True)
    top_10 = []
    for score in scores:
        if len(top_10) < 10:
            top_10.append(score)
        else:
            if score['member_total'] == top_10[-1]['member_total']:
                top_10.append(score)
            else:
                break
    return top_10

top_a = get_top_10(a_scores)
top_b = get_top_10(b_scores)   

print("Top A Scores:")
for score in top_a:
    print(f"  {score['member_name']}: {score['member_total']}")

print("Top B Scores:")
for score in top_b:
    print(f"  {score['member_name']}: {score['member_total']}")

today = date.today()
date_string = today.strftime("%B %Y")

def generate_top_a_html():
    html = ""
    for score in top_a:
        html += f"<tr><td><span style=\"font-size: small;\">{score['member_name']}</span></td><td><span style=\"font-size: small;\">{score['member_total']}</span></td></tr>\n"
    return html

def generate_top_b_html():
    html = ""
    for score in top_b:
        html += f"<tr><td><span style=\"font-size: small;\">{score['member_name']}</span></td><td><span style=\"font-size: small;\">{score['member_total']}</span></td></tr>\n"
    return html

base_html = """
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica; text-align: left; padding-left: 60px;"><span style="font-size: x-large;"><strong><span style="-webkit-font-kerning: none;">""" + date_string + """</span></strong></span></p>
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica;">&nbsp;</p>
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica;"><strong><span style="-webkit-font-kerning: none;">These numbers represent the total points accumulated to date in our monthly competitions.</span></strong></p>
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica;"><strong><span style="-webkit-font-kerning: none;">You can see their high scoring images by returning to the <a href="http://cvillecameraclub.org/node/54">gallery page</a>.</span></strong></p>
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica;">&nbsp;</p>
<table style="height: 385px; ; width: 249px;" border="0">
<tbody>
<tr>
<td style="text-align: center;" colspan="2"><strong><span style="font-size: small;">Top "A" Photographers</span></strong></td>
</tr>""" + generate_top_a_html() + """
</tbody>
</table>
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica;">&nbsp;</p>
<p style="margin-top: 0px; margin-bottom: 0px; font-size: 14px; line-height: normal; font-family: Helvetica;"><span style="font-kerning: none;"><strong>&nbsp;</strong></span></p>
<table style="width: 244px; height: 382px;" border="0">
<tbody>
<tr>
<td style="text-align: center;" colspan="2"><strong><span style="font-size: small;">Top "B" Photographers</span></strong></td>
</tr>""" + generate_top_b_html() + """</tbody>
</table>
"""

print(base_html)