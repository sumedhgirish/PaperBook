import pymupdf as pdfreader
import re, pathlib, sys

class Question:
    def __init__(self, **kwargs):
        self.contents = kwargs

    def __repr__(self):
        return "\n".join(f"{k}: {v}" for k,v in self.contents.items())

    @classmethod
    def from_params(cls, params):
        return cls(**params)

class QuestionPaper:
    def __init__(self, filepath: str, filter_func):
        self.filepath = pathlib.Path(filepath)
        self.document = None
        self.filter_func = filter_func

        self.ques_bank = None

        self._load()

    def _load(self):
        try:
            self.document = pdfreader.Document(self.filepath.as_posix())
            raw_text = ' '.join([page.get_text() for page in self.document.pages()])

            # remove redundant whitepace
            raw_text = re.sub(r"(\s{2,}$)", "", raw_text, flags = (re.I | re.M))
            raw_text = re.sub(r"(?:\ \n)", "\n", raw_text, flags = (re.I | re.M))
            raw_text = re.sub(r"(\s{1,})(?=.)", " ", raw_text, flags = (re.I | re.M))

            questions = self.filter_func(raw_text)
            self.ques_bank = tuple(map(Question.from_params, questions))

        except Exception as err:
            print(f"Could not load Question Paper {self.filepath.name} because {err}")
            sys.exit(1)


if __name__ == "__main__":

    def GATE_filter(text):
        text = re.sub(r"Computer Science and Information Technology \(CS\d\) Organising Institute: .*?Page \d{1,} of \d{1,} ",
           "\n",
           text,
           flags = (re.I | re.M)
        )

        text = re.sub(r"Q\.\d{1,} . Q\.\d{1,} Carry .*? mark Each ",
           "\n",
           text,
           flags = (re.I | re.M)
        )


        # Can we allow for user interaction here?

        lines = re.findall(r"((?:Q\.\d{1,}(.*))(?:\(A\)(.*))(?:\(B\)(.*))(?:\(C\)(.*))(?:\(D\)(.*))$)|(?:Q\.\d{1,}(.*)$)",
                           text, flags = (re.I | re.M))

        questions = []
        for question in lines:
            match (question):
                case ('', '', '', '', '', '', content):
                    questions.append({ "question": content.strip(), "type": "numerical" })

                case (_, content, opta, optb, optc, optd, ''):
                    questions.append({
                        "question": content.strip(),
                        "options": (opta.strip(), optb.strip(), optc.strip(), optd.strip()),
                        "type": "mcq"
                    })

                case _:
                    questions.append({ "raw": question})

        return questions

    paper = QuestionPaper("./files/qps/CS1.pdf", GATE_filter)
    # if paper.ques_bank: print(paper.ques_bank[int(input(">> "))])
    print(len(paper.ques_bank))

    sys.exit()
