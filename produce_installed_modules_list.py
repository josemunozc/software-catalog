#!/usr/bin/env python
import pandas as pd 
import argparse
import os.path
import re
import subprocess
import csv
import matplotlib.pyplot as plt
import numpy as np
plt.switch_backend('agg')

parser = argparse.ArgumentParser(description='Create a list of installed modules with descriptions')
parser.add_argument("-t","--theme", dest='theme', metavar='THEME',
                    required=False,help='select application theme to produce list',
                    choices=["all","chemistry","genomics"],
                    default="all")
args = parser.parse_args()

# define a couple of variables 'themes' and 'match_pattern' based on default or 
# user passed options. 'themes' defines what application fields should be taken
# into account; 'match_pattern' defines what pattern is used to search for module
# files in the application fields.
if args.theme == 'all':
    themes=['biology','chemistry','compilers','creative','environment','financial',
            'genomics','languages','libraries','machine-learning','materials',
            'medical','physics','tools']
    match_pattern="/apps/modules/*"
else:
    themes=[args.theme]
    match_pattern="/apps/modules/"+args.theme

# function to list the content of a directory, returns a list with the output of
# bash command 'ls -1 directory', so it would work better if passed an absolute
# path
def list_directory_content(directory):
    bashCommand="ls -1 " + directory
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE,
            universal_newlines=True)
    output, error = process.communicate()
    return(output)

def pie_chart(number_of_apps_list):
    # search for zeros and mark the indices
    zeros_indexes=[i for i, e in enumerate(number_of_apps_list) if e == 0]
    # remove elements with 0 apps
    labels=themes
    for i in sorted(zeros_indexes,reverse=True):
        del labels[i]
        del number_of_apps_list[i]
    total_apps=sum(number_of_apps_list)
    sizes=[float(app)/total_apps for app in number_of_apps_list]

    fig, ax = plt.subplots(figsize=(9, 4), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(sizes, labels=None, wedgeprops=dict(width=0.5),
                           startangle=0)
    ax.legend(wedges, labels, title="Areas",loc="lower left",bbox_to_anchor=(1.2,0))

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        if sizes[i] > 0.03:
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate('{0}%'.format(100*round(sizes[i],3)), xy=(x, y), 
                    xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)
    
    ax.set_title("Distribution of Hawk available modules",
            fontdict={'fontsize':14})
    plt.savefig('pie_chart.svg')

#def func(pct, allvals):
#    absolute = int(pct/100.*np.sum(allvals))
#    return "{:.1f}%\n({:d} g)".format(pct, absolute)


# The main loop that searches for modules files in the application directories.
# It iterates through the fields defined in 'themes'
# Special case: 'compilers' - the structure for this directory includes an additional
# 'compiler' directory that needs to be included.
number_of_apps_list=[]
for t in themes:
    root='/apps/modules/'+t
    if t=="compilers":
        root='/apps/modules/'+t+'/compiler'
    root_directory_content=list_directory_content(root)
    number_of_apps=len(root_directory_content.splitlines());
    number_of_apps_list.append(number_of_apps)

    print('## {0}'.format(t))
    print('|Name|Versions available|Description|')
    print('|----|------------------|-----------|')
    #print('{0}\t{1}'.format(t,number_of_apps))
    for app in root_directory_content.splitlines():
        versions=list_directory_content(root+'/'+app)
        #print(app)
        #print(versions.splitlines())
        # Instead of looping through all versions for the same app and parse their
        # help text, we only do it for the first one. This assumes that the help text
        # is similar (same?) across versions.
        #for v in versions.splitlines():
        if len(versions.splitlines()):
            module_file=root+"/"+app+"/"+versions.splitlines()[0]
            if os.path.isfile(module_file):
                f = open(module_file,'r')
                content = f.read()
                help_text=re.findall('^set help_text(.*)',content,re.M)
                if len(help_text)>0:
                    help_text_string=re.sub('.*"\\\\t','',help_text[0])
                    
                    print('|{0}|{1}|{2}|'.format(app,
                        ' ,'.join(versions.splitlines()),help_text_string))
                    #print '\t{0}\t{1}\t{2}'.format(app,help_text_string,
                    #        ' ,'.join(versions.splitlines()))
                else:
                    print('|{0}|{1}|missing description|'.format(app,
                        ' ,'.join(versions.splitlines()),help_text_string))
                    #print '\t{0}\t{1}'.format(app,"missing description",
                    #        ' ,'.join(versions.splitlines()))
            else:
                print '{0}\t{1}'.format(module_file,"not a file")

pie_chart(number_of_apps_list)
