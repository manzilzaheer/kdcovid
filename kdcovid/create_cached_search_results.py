from kdcovid.search_tool import SearchTool
from kdcovid.task_questions import TaskQuestions

import pickle

from absl import flags
from absl import app
from absl import logging

FLAGS = flags.FLAGS

flags.DEFINE_string('data_dir', '2020-04-10', 'data path')
flags.DEFINE_string('out_dir', '2020-04-10', 'out path')
flags.DEFINE_string('css_file', 'style.css', 'css_file')
flags.DEFINE_string('paper_id', 'cord_uid', 'cord_uid or sha')
flags.DEFINE_string('results', None, 'results pickle')

logging.set_verbosity(logging.INFO)


def format_task_html(task2subtasks, subtasks_html):
    s = ""
    s += "<BR/><BR/><h1>Queries for Provided Questions per Task:</h1><BR/>"
    for t, subtasks in task2subtasks.items():
            s += """<br><br><button type="button" class="collapsible"><b>{}</b></button><div class="content">{}</div>""".format(
                t, format_subtask_html(subtasks, subtasks_html))
    return s


def format_subtask_html(subtasks, subtasks_html):
    r = ''
    for st, _, _ in subtasks:
        r += """<br><br><button type="button" class="collapsible">{}</button>
            <div class="content1">
              <p>{}</p>
            </div>""".format(st, subtasks_html[st])
    return r

def format_example_queries(example_queries, queries_html, css):
    html_string = """
    <!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="./style.css">
    <link rel="icon" type="image/ico" href="./favicon.ico">
    <link rel="stylesheet" href="https://use.typekit.net/wtq0evn.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    INSERT_CSS

    .collapsible {
      background-color: white;
      color: #3E4550;
      border-radius: 7px;
      cursor: pointer;
      padding: 18px;
      text-align: center;
      width: 100%
      outline: none;
      font-size: 18px;
      border-style: solid;
      border-color: #3E4550;
      font-family: 'Basic Sans', sans-serif;
    }

    .active, .collapsible:hover {
      background-color: rgb(36.1472, 145.5616, 241.9456);
      color: white;
    }


    .content1 {
      padding: 0 18px;
      display: none;
      overflow: hidden;
      background-color: #f1f1f1;
      font-size: 15px;
      font-family: 'Basic Sans', sans-serif;
      text-align: left;
    }

    .content {
      padding: 0 18px;
      display: none;
      overflow: hidden;
      background-color: #f1f1f1;
      font-size: 15px;
      font-family: 'Basic Sans', sans-serif;
      text-align: center;
    }

    </style>
    </head>
    <body>


    CONTENT

    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
          content.style.display = "none";
        } else {
          content.style.display = "block";
        }
      });
    }
    </script>

    </body>
    </html>
    """.replace('CONTENT', format_subtask_html(example_queries, queries_html)).replace('INSERT_CSS', css)
    return html_string

def format_tasks(task2subtasks, subtasks_html, css):

    html_string = """
    <!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="./style.css">
    <link rel="icon" type="image/ico" href="./favicon.ico">
    <link rel="stylesheet" href="https://use.typekit.net/wtq0evn.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    INSERT_CSS
   
    .collapsible {
      background-color: white;
      color: #3E4550;
      border-radius: 7px;
      cursor: pointer;
      padding: 18px;
      text-align: center;
      width: 100%
      outline: none;
      font-size: 18px;
      border-style: solid;
      border-color: #3E4550;
      font-family: 'Basic Sans', sans-serif;
    }
    
    .collapsible1 {
      background-color: white;
      color: #3E4550;
      border-radius: 7px;
      cursor: pointer;
      padding: 18px;
      text-align: left;
      width: 100%
      outline: none;
      font-size: 18px;
      border-style: solid;
      border-color: #3E4550;
      font-family: 'Basic Sans', sans-serif;
    }


    .active, .collapsible:hover {
      background-color: rgb(36.1472, 145.5616, 241.9456);
      color: white;
    }


    .content1 {
      padding: 0 18px;
      display: none;
      overflow: hidden;
      background-color: #f1f1f1;
      font-size: 15px;
      font-family: 'Basic Sans', sans-serif;
      text-align: left;
    }

    .content {
      padding: 0 18px;
      display: none;
      overflow: hidden;
      background-color: #f1f1f1;
      font-size: 15px;
      font-family: 'Basic Sans', sans-serif;
      text-align: center`;
    }

    </style>
    </head>
    <body>
    
    
    CONTENT
    
    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;
    
    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
          content.style.display = "none";
        } else {
          content.style.display = "block";
        }
      });
    }
    </script>
    
    </body>
    </html>
    """.replace('CONTENT', format_task_html(task2subtasks, subtasks_html)).replace('INSERT_CSS', css)
    return html_string


def main(argv):
    logging.info('Running create_cached_search_results with arguments: %s', str(argv))

    with open(FLAGS.css_file, 'r') as fin:
        css = '\n'.join([x for x in fin])
        task_questions = TaskQuestions()

    if FLAGS.results is None:
        search_tool = SearchTool(data_dir=FLAGS.data_dir, paper_id_field=FLAGS.paper_id)
        from collections import defaultdict
        results = defaultdict(str)
        for task, questions in task_questions.task2questions.items():
            for q, recent, covid in questions:
                html_res = search_tool.get_search_results(q, recent, covid)
                results[q] = html_res

        for q, recent, covid in task_questions.example_queries:
            html_res = search_tool.get_search_results(q, recent, covid)
            results[q] = html_res

        with open(FLAGS.out_dir + '/cached_results.pkl', 'wb') as fout:
            pickle.dump(results, fout)
    else:
        with open(FLAGS.results, 'rb') as fin:
            results = pickle.load(fin)

    html_output = format_tasks(task_questions.task2questions, results, css)



    with open(FLAGS.out_dir + "/tasks.html", 'w') as fout:
        fout.write(html_output)

    html_examples = format_example_queries(task_questions.example_queries, results, css)
    with open(FLAGS.out_dir + "/examples.html", 'w') as fout:
        fout.write(html_examples)


if __name__ == '__main__':
    app.run(main)
