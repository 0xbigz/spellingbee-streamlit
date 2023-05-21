import streamlit as st
import numpy as np


RULES_STR = """

Words must contain at least 4 letters.\n
Words must include the center letter. \n
Letters can be used more than once. \n
4-letter words are worth 1 point each. \n
Longer words earn 1 point per letter. \n
Each puzzle includes at least one “pangram” which uses every letter. These are worth 7 extra points! \n
"""

st.cache(persist=True)
def load_word_list():
    return np.loadtxt('words_alpha.txt', dtype=str)

st.cache(persist=True)
def filter_words(word_list, letter_list):
    # Convert the letter_list to lower case for case insensitivity
    letter_set = set([letter.lower() for letter in letter_list])
    filtered_list = []

    for word in word_list:
        # Convert word to lower case for case insensitivity
        word_lower = word.lower()

        if len(word_lower) >= 4 and set(word_lower).issubset(letter_set) and letter_list[0] in word_lower:
            filtered_list.append(word)

    return filtered_list

def pangram_words(word_list, letter_list):
    # Convert the letter_list to lower case for case insensitivity
    letter_list = [letter.lower() for letter in letter_list]
    pangram_words = []

    for word in word_list:
        # Convert word to lower case for case insensitivity
        word_lower = word.lower()

        if all(letter in word_lower for letter in letter_list):
            pangram_words.append(word)

    return pangram_words

def draw_letters(letters, c1, c2, c3):
    letters = [l.upper() for l in letters]
    c1.write('')
    c2.write(letters[2])
    c3.write('')
    c3.write()

    c1.write(letters[1])
    c3.write(letters[3])
    c2.markdown(
        '<span style="color:yellow">'+letters[0]+'</span>',    unsafe_allow_html=True    
        )
    c1.write(letters[4])
    c3.write(letters[5])
    c2.write(letters[6])


def find_game():
    lowercase_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    lls = list(set(np.random.random_integers(0, len(lowercase_letters)-1, 7)))
    count = 0
    while len(lls)<7:
        lls += [count % 26]
        lls = list(set(lls))
        count+=1

    letters = list(set([lowercase_letters[x] for x in lls]))

    words = load_word_list()

    answers = filter_words(words, letters)
    supwords = pangram_words(answers, letters)

    return letters, answers, supwords



def reset_state():
    if 'in_a_game' not in st.session_state:
        letters, words, pangrams = find_game()
        st.session_state['in_a_game'] = True

        if 'letters' not in st.session_state:
            st.session_state['letters'] = letters

        if 'words' not in st.session_state:
            st.session_state['words'] = words

        if 'pangrams' not in st.session_state:
            st.session_state['pangrams'] = pangrams

        if 'score' not in st.session_state:
            score = 0
            st.session_state['score'] = score

        if 'answers' not in st.session_state:
            st.session_state['answers'] = []

def main():
    st.set_page_config(
        'Spelling Bee',
        # layout='wide',
        page_icon="🐝"
    )
    b1, b2 = st.sidebar.columns(2)
    if b1.button('New Pangram'):
        st.cache_data.clear()
        st.session_state.clear()
        while 'pangrams' not in st.session_state or len(st.session_state['pangrams'])<1:
            st.session_state.clear()
            reset_state()
            print(st.session_state['pangrams'])
    if b2.button('New Game'):
        st.cache_data.clear()
        st.session_state.clear()
        reset_state()
    
    st.header('Spelling Bee 🐝')
    reset_state()
    # st.write(st.session_state['letters'])
    guesscol, anscol = st.columns([15, 5])

    # st.sidebar.json(st.session_state, expanded=False)

    guess = guesscol.text_input('guess:', )
    _, c1, c2, c3, _ = guesscol.columns([10, 1,1,1, 10])


    def redraw_letters():
        draw_letters(st.session_state['letters'], c1, c2, c3)


    # draw_letters(st.session_state['letters'], c1, c2, c3)
    redraw_letters()
    # e1,e2,e3 = guesscol.columns([1,1,1])
    # e1.button('delete')
    # guesscol.button('🔄', use_container_width=True, on_click=redraw_letters)
    # e3.button('enter', help='mommy')
    warningbox = guesscol.container()
    warningbox.write('')


    # aw, sw = st.sidebar.columns(2)
    with st.sidebar.expander('available words: ' + str(len(st.session_state['words']))):
        st.json(st.session_state['words'], expanded=True)
    with st.sidebar.expander('pangrams: ' + str(len(st.session_state['pangrams']))):
        st.json(st.session_state['pangrams'], expanded=True)

    is_long_enough = len(guess) >= 4
    is_word = guess in st.session_state['words']
    is_pangram = guess in st.session_state['pangrams']
    contains_middle = st.session_state['letters'][0] in guess
    not_prev_guess = guess not in st.session_state['answers']

    is_valid = is_long_enough and contains_middle and not_prev_guess and is_word
    if guess!='':
        if is_valid and is_pangram:
            st.balloons()
            st.session_state['score'] += max(0, len(guess)-3 + 7)
            st.session_state['answers'].append(guess)
        elif is_valid:
            st.session_state['score'] += max(0, len(guess)-3)
            st.session_state['answers'].append(guess)
        elif not is_long_enough:
            warningbox.warning('word not long enough')
        elif not contains_middle:
            warningbox.warning('word doesnt contain: "' + st.session_state['letters'][0]+'"')
        elif not is_word:
            non_overlap = set(guess) - set(guess).intersection(st.session_state['letters'])
            if non_overlap:
                warningbox.warning('contains excess letters: ' +str(non_overlap))
            else:
                warningbox.warning('not valid dictionary word')
        elif not not_prev_guess:
            warningbox.warning('you already found this word')

    current_score = st.session_state['score']

    level = 'Beginner'
    if current_score < 4 and current_score > 1:
        level = 'Meh'
    elif current_score > 100:
        level = 'Genius'
    elif current_score > 88:
        level = 'Amazing'
    elif current_score > 69:
        level = 'Great'
    elif current_score > 42:
        level = 'Solid'
    elif current_score > 25:
        level = 'Good'
    elif current_score > 10:
        level = 'Moving Up'



    anscol.progress(min(current_score, 100), text=level)
    anscol.button('score: ' + str(current_score),
                  disabled=False,
                  help=RULES_STR)
    num_found = len(st.session_state['answers'])
    if num_found:
        anscol.write('You found '+ str(num_found) + ' words!')
        count = 0
        ff = st.session_state['answers']
        ff = list(reversed(ff))
        for x in ff:
            anscol.write('- '+x)
            count+=1
            if count>=5:
                break
        if count >= 5:
            with anscol.expander('see more...'):
                for x in ff[5:]:
                    st.write('- '+x)




if __name__ == '__main__':
    main()