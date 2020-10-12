#!/usr/bin/python3.8
"""
Author: Alexandra DeLucia
"""
import re


# Settings
output_file = "survey.html"
num_narratives = 6

metrics_dict = {
    "interesting": {
        "question": "How <b>interesting</b> is the story?",
        "definition": "The story is fun to read. It feels creative, original, dynamic, and/or vivid. The opposite of this might be something that's obvious, stereotypical/unoriginal, and/or boring.",
        "options": {
            4: {
                "label": "Very interesting",
                "definition": "The story has themes, characters, and dialog that make you <b>want to keep reading it</b> and you might even want to show it to a friend"
            },
            3: {
                "label": "Somewhat interesting",
                "definition": "The story has themes, characters, dialog, and/or a writing style that <b>pique your interest</b>"
                },
            2: {
                "label": "Not very interesting",
                "definition": "You finish the story but can't remember anything unique about it. Good enough, but <b>not a fun read</b>"
                },
            1: {
                "label": "Not at all interesting",
                "definition": "You do not even want to finish reading the story. It is <b>boring</b> and/or unoriginal."
                }
        }
    },
    "fluent": {
        "question": "How <b>fluent</b> is the story?",
        "definition": """The story is written in grammatical English. No obvious grammar mistakes that a person wouldn't make. <b>An incomplete final word or incomplete sentence does not count as a mistake and should not affect fluency</b>. The English sounds natural. Note: do not take off points for spaces between punction (e.g. "don 't") and simpler sentences. Simple English is as good as complex English, as long as everything is grammatical.""",
        "options": {
            4: {
                "label": "Very fluent",
                "definition": "The sentences read as if they were <b>written by a native English speaker with 1 or no errors.</b>"
            },
            3: {
                "label": "Somewhat fluent",
                "definition": "The sentences read as if they were written by a <b>native English speaker with very few errors</b>. Some minor mistakes that a person could have reasonably made."
                },
            2: {
                "label": "Not very fluent",
                "definition": "Many sentences have <b>frequently repeated words and phrases</b>. Obvious mistakes."
                },
            1: {
                "label": "Not at all fluent",
                "definition": "The sentences are <b>completely unreadable</b>. If the same sentence is <b>repeated over and over</b> for the entire story, that story is considered not at all fluent."
                }
        }
    },
    "coherent": {
        "question": "How <b>coherent</b> is the story?",
        "definition": "The story feels like one consistent story, and not a bunch of jumbled topics. Stays on-topic with a consistent plot, and doesn't feel like a series of disconnected sentences.",
        "options": {
            4: {
                "label": "Very coherent",
                "definition": "The sentences when taken as a whole all have a </b>clearly identifiable plot</b>"
            },
            3: {
                "label": "Somewhat coherent",
                "definition": "Many of the sentences work together for a <b>common plot</b> with common characters. One or two unrelated sentences."
                },
            2: {
                "label": "Not very coherent",
                "definition": "Only a few sentences seem to be from the same story; the others are random."
                },
            1: {
                "label": "Not at all coherent",
                "definition": "There is absolutely <b>no identifiable plot</b>. Each sentence feels <b>completely disconnected</b> from every other sentence."
                }
        }
    },
    "relevant": {
        "question": "How <b>relevant</b> is the story <b>to the prompt</b>?",
        "definition": "How closely the story builds from the prompt.",
        "options": {
            4: {
                "label": "Very relevant",
                "definition": "It is very clear the story follows the prompt from the theme, vocabulary, and specific plot events.",
                },
            3: {
                "label": "Somewhat relevant",
                "definition": "A few sentences directly mention themes or vocabulary from the prompt.",
                },
            2: {
                "label": "Not very relevant",
                "definition": "The theme of the prompt is somewhat apparent in the story, but involves a stretch of the imagination.",
                },
            1: {
                "label": "Not at all relevant",
                "definition": "It is as if the story were written without reading the prompt.",
                }
        }
    }
}

narrative_examples = [
        # for_human_0.5 #2)
        {
            "prompt": "The apocalypse has come . The only survivors : a young child , and the monster under the bed ...",
            "story": "AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
            "comment": "This story is not at all interesting, fluent, or coherent. It is only repetitive which is a sign of a degenerate model. However, it is not very relevant to the prompt since it is only a scream, which sort of relates to the setup of a child with a monster under the bed.",
            "answers": {
                "interesting": 1,
                "fluent": 1,
                "coherent": 1,
                "relevant": 2,
                }
        },
        # (for_human 0.3 #1)
        {
            "prompt": "Write the last paragraph of a science fiction epic .",
            "story": "The white coat stared at the man in the black suit.<br>`` What are you doing here? ''<br>`` I'm here to get the answers to the question you've been asking me for the last two days. ''",
            "comment": "This story is very interesting (what are the answers???), very fluent (no grammatical errors), and very coherent (the plot is a confrontation between two characters). Also, the story is somewhat relevant because it uses words in the theme of science fiction (i.e. 'white coat', 'black suit') and this confrontation could take place at the end of an epic.",
            "answers": {
                "interesting": 4,
                "fluent": 4,
                "coherent": 4,
                "relevant": 3,
            }
        },
        # (for_human 0.9 #2)
        {
            "prompt": "The apocalypse has come . The only survivors : a young child , and the monster under the bed ...",
            "story": "Time seemed to float by him, an uncomfortable flicker of light. Taking a quick glance in the mirror, he was awed at how pale he looked. His skin looked swollen and red. He lay back in bed, feeling defeated and defeated. Then he sighed and went to his bedroom, stretched his arms, and ran his hands through his hair.<br><br>He couldn't wait to get back to sleep. He had a routine, like the people he used to hang out with before they were hit by mass suicide. He took his shower, washed himself, and put on his hoodie. He took his clothes off and put them in the closet in his room. He went out and looked for his favorite stuffed animal, that his mother would love. It was her favorite, that was a hiss. He stepped outside and came back to see how things were going. The world wasn't going to end, but he knew there was a chance of a very mild devastation. To his amazement, the planet had finally released it's dormant population. Not yet.<br><br>He thought to himself, I guess I 'll be the first to show up. Maybe wit",
            "comment": 'This story is very interesting, very fluent, and somewhat coherent. It is interesting because of the central apocalyptic theme, with "mass suicide" and "dormant population." The story is very fluent because there are no grammatical errors, and only one repetition, "defeated and defeated." The story is somewhat coherent because there is a general plot of a boy waking up and getting ready in a post-apocalyptic world, but some of the sentences are contradictory (i.e. "He took his shower, washed himself, and put on his hoodie. He took his clothes off and put them in the closet in his room" and "He stepped outside and came back") or do not make sense (i.e. "It was her favorite, that was a hiss"). The story is very relevant because it is clear the narrator is a child from the stuffed animals, and the apocalyptic theme is followed.',
            "answers": {
                "interesting": 4,
                "fluent": 4,
                "coherent": 3,
                "relevant": 4,
            }
        },
        # (for_human 1.0 #1)
        {
            "prompt": "Write the last paragraph of a science fiction epic .",
            "story": '"Commander Rex" a voice calls out once we reach the top of the ship "With the force hovering above us reaching ninety percent within three hundred hours we can unleash the full extent of our scientific resources...''<br><br>"... if your research was confiscated we \'d have to spend five years working on a new protocol "<br><br>" I was told, Ambassador Cornwell that is why I have to go overboard "',
            "comment": "This story is very interesting (what will they do with their scientific resources???), very fluent (no grammatical errors), and somewhat coherent (the sentences all seem like they are from the same story). It is also very relevant from the discussion of ships, hovering, 'scientific resources', etc.",
            "answers": {
                "interesting": 4,
                "fluent": 4,
                "coherent": 3,
                "relevant": 4
                }
        },
    ]

# Helper methods
def create_option_list(item_id, metric, answer=None):
    metric_info = metrics_dict[metric]
    # Question
    hover_label = re.sub("<\/?\w{1,}>", "", metric_info["definition"])
    hover_label = re.sub("\"", "'", hover_label)
    output = f"<p><span title=\"{hover_label}\">{metric_info['question']}</span></p>\n"
    
    # Create the radio buttons with labels above the button
    output += '<div class="container">\n<div class="row justify-content-center">'
    for value, info in metric_info["options"].items():
        # Hover label is the metric definition
        # remove <b>/<u> styles
        hover_label = re.sub("<\/?\w{1,}>", "", info["definition"])
        output += f'<div class="col-sm text-center" title="{hover_label}">\n'
        # Row for label
        output += f'<div class="row justify-content-center"><label for="{item_id}-{metric}-{value}">{info["label"]}</label></div>\n'
        # Row for button
        # Fill in answer if given (used for examples)
        if answer:
            output += f'<div class="row justify-content-center"><input id="{item_id}-{metric}-{value}" type="radio" name="{item_id}-{metric}" value={value} {"checked" if answer==value else "disabled"}></div>\n'
        else:
            output += f'<div class="row justify-content-center"><input id="{item_id}-{metric}-{value}" type="radio" name="{item_id}-{metric}" value={value} required></div>\n'
        # Close column
        output += '</div>\n'
    # Close row and container
    output += '</div></div><br>\n'
    return output


def create_evaluation_display(item_id, answers={}):
    """
    Use answers dict for demo examples
    """
    output = ""
    for metric in metrics_dict.keys():
        output += create_option_list(item_id, metric, answers.get(metric))
    return output


def create_narrative_display(display_num, item_id, story):
    output = f"""<!-- Response {display_num} -->
    <div>
    <!-- Display generated response -->
    <h3>Narrative {display_num}</h3>
    <p class="story">{story}</p>
    <br/>
    <h4>Evaluation</h4>
    {create_evaluation_display(item_id)}
    </div>
    """
    return output


def create_examples_display():
    output = ""
    for i, example in enumerate(narrative_examples):
        title = f"demo{i}"
        output += f"""<div>
        <h3>Demo Narrative {i+1}</h3>
        <p class='story'>[PROMPT] {example["prompt"]}<br><br>[RESPONSE] {example["story"]}</p>
        <br/>
        <h4>Evaluation</h4>
        <p><b>Comment:</b> {example["comment"]}</p>
        <br/>
        {create_evaluation_display(title, example["answers"])}
        </div><hr>
        """
    return output


header = """<!DOCTYPE html>
<!-- You must include this JavaScript file -->
<script src="https://assets.crowd.aws/crowd-html-elements.js"></script>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">

<!-- Custom styling -->
<style>
    body {
        width: 90%;
        margin: 0 auto;
    }
    .story {
        font-family: Consolas,"courier new";
        overflow-wrap: anywhere;
        width: 85%;
        margin: 0 auto;
        background-color: #F0F0F0;
        padding: 5px;
    }
    hr {
        border-top: 5px solid #8c8b8b;
    }
    input[type=radio] {
        width: 20px;
        height: 20px;
    }
    .red {
        color: red;
    }
</style>


<!-- For the full list of available Crowd HTML Elements and their input/output documentation,
    please refer to https://docs.aws.amazon.com/sagemaker/latest/dg/sms-ui-template-reference.html -->

<!-- You must include crowd-form so that your task submits answers to MTurk -->
<crowd-form answer-format="flatten-objects">
<br/>
"""

definitions = """<h3>Definitions</h3>
Below you will find multiple prompts and stories (narratives) generated from those prompts. Please rate the stories according to their interestingness, fluency, coherence, and relevance following the given definitions and examples. We will reject your HIT if you input obviously wrong answers.
<br>
The 5-point scale for each definition should be used as a guideline. <u>The definitions are displayed when hovering over each radio button for convenience.</u> (Note: if the definitions do not appear even after a few seconds, please leave your browser (e.g. Chrome) and OS (e.g. Windows) information in the comment box.)
<br><br>
"""

definitions += "<ul>\n"
for metric, info in metrics_dict.items():
    definitions += f"<li><b>{metric.capitalize()}:</b>{info['definition']}\n"
    definitions += "<ul>"
    for value, value_info in info["options"].items():
        definitions += f"<li><u>{value_info['label']}:</u> {value_info['definition']}</li>\n"
    definitions += "</ul></li><br>\n"
definitions += "</ul>\n"

footer = """
</crowd-form>
<!-- End -->
</html>
"""

worker_verifications = f"""
<h3>Please confirm the following worker criteria:</h3>
    <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" id="worker-read-instructions" name="worker-read-instructions" type="checkbox" required>I have read the instructions</label>
    </div>
    <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" id="worker-read-examples" name="worker-read-examples" type="checkbox" required>I have read the examples</label>
    </div>
    <div class="form-check">
        <label class="form-check-label"><input class="form-check-input" id="worker-english-speaker" name="worker-english-speaker" type="checkbox" required>I am a native English speaker</label>
    </div>
"""

# Create the HTML file
narrative_displays = '<hr>\n'.join([create_narrative_display(i+1, f"story_{i}", f"[PROMPT] ${{prompt_{i}}}<br><br>[RESPONSE] ${{response_{i}}}") for i in range(num_narratives)])
output = f"""
{header}
<!-- Instructions -->
<crowd-tabs>
<crowd-tab header="Detailed Instructions">
<p class="red">We will reject your HIT if you fail attention checks or if you have unusually low agreement with other annotators.</p>

{definitions}
</crowd-tab>
<crowd-tab header="Examples">
{create_examples_display()}
</crowd-tabs>
<hr>
{worker_verifications}
<hr>
{narrative_displays}
<hr>
<!-- Worker feedback -->
<p>Enter any comments or feedback about this survey below (optional).</p>
<textarea class="form-control" name="worker-comments" rows="3"></textarea>
<br>
{footer}
"""

with open(output_file, "w+") as f:
    f.write(output)


