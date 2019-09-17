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
                    question = {
                        'type': 'input',
                        'name': i,
                        'message': q['msg'],
                    }

                    if 'default' in q:
                        question['default'] = q['default']

                    questions.append(question)

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
                val = answers[i]

                # Convert value if conversion function provided
                if 'conv' in self.additional_questions[i]:
                    val = self.additional_questions[i]['conv'](val)

                values.append(val)

            # Optional values
            opt = {}
            for name, i in optional_questions:
                val = answers[i]

                # Convert value if conversion function provided
                if 'conv' in self.additional_questions[i]:
                    val = self.additional_questions[i]['conv'](val)

                opt[name] = val

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
    def loop(root_menu, exit_confirmation=True):
        menu = root_menu
        try:
            while True:
                menu = menu.show()
                if menu is None:
                    if not exit_confirmation:
                        break

                    # Exit confirmation
                    questions = [{'type': 'confirm',
                                  'message': 'Are you sure you want to quit?',
                                  'name': 'quit',
                                  'default': True}]
                    answers = prompt(questions)
                    if answers['quit']:
                        break
                    else:
                        menu = root_menu

        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    # Compact method
    def handler(filepath, number, choices, opt_var=None):
        print('')
        print('filepath:\t{}\t\ttype:\t\t{}'.format(filepath, type(filepath)))
        print('number:\t\t{}\t\t\ttype:\t\t{}'.format(number, type(number)))
        print('choices:\t{}\ttype:\t\t{}'.format(choices, type(choices)))
        print('opt_var:\t{}\t\ttype:\t\t{}'.format(opt_var, type(opt_var)))
        print('')

    root_menu = Menu('Root')
    root_menu.add_children([
    Menu('Top Level 1',
         children=[
             MenuItem('Mid Level 1 Item',
                      lambda: print('Mid Level 1 Item called')),
             MenuItem('Mid Level 2 Item',
                      lambda: print('Mid Level 2 Item called'))
         ]),

    Menu('Top Level 2',
         has_back=False,
         children=[
             MenuItem('Mid Level 3 Item',
                      lambda: print('Mid Level 3 Item called')),
             Menu('Mid Level 4 Menu',
                  children=[
                      MenuItem('Bottom Level 1 Item',
                               lambda: print('Bottom Level 1 Item called')),
                      MenuItem('Additional questions test',
                               handler,
                               additional_questions=[
                                   {'msg': 'Enter file path.'}, # Note missing 'type' that defaults to 'input'
                                   {'msg': 'Enter a number.',
                                    'conv': int, # Converts to integer
                                    'default': '15'},
                                   {'type': 'checkbox', # Note missing 'msg'
                                    'choices': ['choice1', 'choice2']},
                                   {'msg': 'Enter a value.',
                                    'once': True,
                                    'name': 'opt_var'}
                               ])

                  ])

         ])
    ])

    Menu.loop(root_menu)
