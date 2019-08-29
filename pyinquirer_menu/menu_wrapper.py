from PyInquirer import prompt

class MenuItem():
    def __init__(self, text, handler, parent=None, additional_questions=None, menu_after=None):
        self.text = text
        self.handler = handler
        self.parent = parent
        self.menu_after = menu_after

        self.additional_questions = additional_questions

        if additional_questions is not None:
            self.additional_question_counts = [0 for i in additional_questions]

    def handle_selection(self):
        if self.additional_questions is not None:
            asked_indices = []
            questions = []
            optional_questions = []
            for i, q in enumerate(self.additional_questions):
                # Check if we should ask this question
                optional_question = False
                if 'once' in q and q['once']:
                    optional_question = True
                    if self.additional_question_counts[i] > 0:
                        # Don't ask
                        continue

                # Handle input type (the default type)
                if 'type' not in q or q['type'] == 'input':
                    questions.append({
                        'type': 'input',
                        'name': i,
                        'message': q['msg']
                    })

                # Handle checkbox question
                elif q['type'] == 'checkbox':
                    choices = [{'name': c} for c in q['choices']]

                    if 'msg' in q:
                        msg = q['msg']
                    else:
                        msg = 'Select option(s)'

                    questions.append({
                        'type': 'checkbox',
                        'message': msg,
                        'name': i,
                        'choices': choices
                    })

                self.additional_question_counts[i] += 1

                if optional_question:
                    optional_questions.append((q['name'], i))
                else:
                    asked_indices.append(i)

            answers = prompt(questions)

            # Required values
            values = []
            for i in asked_indices:
                values.append(answers[i])

            # Optional values
            opt = {}
            for name, i in optional_questions:
                opt[name] = answers[i]

            self.handler(*values, **opt)

        else:
            self.handler()

class Menu():
    def __init__(self, text, children=None, parent=None, prompt_text='Choose option.', has_back=True):
        self.children = None
        self.text = text
        self.has_back = has_back
        self.prompt_text = prompt_text
        self.parent = parent

        if children is not None:
            self.add_children(children)

    def add_children(self, children):
        if self.children is None:
            self.children = []

        for child in children:
            child.parent = self
            self.children.append(child)

            # menu_after parent for menu_item
            if isinstance(child, MenuItem) and child.menu_after:
                if child.menu_after.has_back:
                    child.menu_after.parent = child
                else:
                    child.menu_after.parent = self

    def get_questions(self):
        choices = [x.text for x in self.children]

        if self.has_back:
            choices.append('Back')

        questions = [
            {
                'type': 'list',
                'name': 'q',
                'message': self.prompt_text,
                'choices': choices
            }
        ]

        return questions

    def show(self):
        questions = self.get_questions()
        answers = prompt(questions)

        if answers['q'] == 'Back':
            # Check if parent has back
            if self.parent and not self.parent.has_back:
                return self.parent.parent

            return self.parent

        # Match answer to child
        child = None
        for c in self.children:
            if c.text == answers['q']:
                child = c

        if child is None:
            raise Exception('Invalid selection.')

        if isinstance(child, Menu):
            return child
        elif isinstance(child, MenuItem):
            child.handle_selection()

            if child.menu_after:
                return child.menu_after
            if not self.has_back:
                return self.parent
            else:
                return self

    @staticmethod
    def loop(root_menu):
        menu = root_menu
        try:
            while True:
                menu = menu.show()
                if menu is None:
                    break
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    def load_handler(filepath, length, choices):
        print('Loadhandler called with path: {} and length: {} and choices: {}'.format(filepath,
                                                                                       length,
                                                                                       choices))
    # Compact method
    root_menu = Menu('Root')
    root_menu.add_children([
        Menu('RL',
             children=[
                 MenuItem('Do RL',
                          lambda: print('Do RL called')),
                 MenuItem('Something else',
                          lambda: print('Something else called'))
             ]),

        Menu('IRL',
             has_back=False,
             children=[
                 MenuItem('Do IRL',
                          lambda: print('Do IRL called')),
                 Menu('Reward',
                      children=[
                          MenuItem('Load',
                                   load_handler,
                                   additional_questions=[
                                       {'msg': 'Enter file path'},
                                       {'msg': 'Enter length.'},
                                       {'type': 'checkbox',
                                        'choices': ['reward_per_episode',
                                                    'total_reward']}
                                   ]),
                          MenuItem('Save',
                                   lambda x, opt_var=None: print('Got: {} {}'.format(x, opt_var)),
                                   additional_questions=[
                                       {'msg': 'Enter file path',
                                        'once': True,
                                        'name': 'opt_var'},
                                       {'type': 'checkbox',
                                        'msg': 'Some message',
                                        'choices': ['one', 'two', 'three']}
                                   ])

                      ])

             ])
    ])

    Menu.loop(root_menu)
