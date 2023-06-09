import streamlit as st
import numpy as np
import datetime
import random
RULES_STR = """

Words must contain at least 4 letters.\n
Words must include the center letter. \n
Letters can be used more than once. \n
4-letter words are worth 1 point each. \n
Longer words earn 1 point per letter. \n
Each puzzle includes at least one “pangram” which uses every letter. These are worth 7 extra points! \n
"""

def on_the_hour_ts():
    # Get the current UTC time
    current_time = datetime.datetime.utcnow()

    # Round down to the closest hour
    rounded_time = current_time.replace(minute=0, second=0, microsecond=0)

    # Convert the rounded time to a Unix timestamp
    timestamp = int(rounded_time.timestamp())

    return (timestamp)

@st.cache_data(persist=True)
def load_word_list():
    return np.loadtxt('words_alpha.txt', dtype=str)

@st.cache_data(ttl=3600)
def load_hourly_letters(ts):
    tt = ts
    man_letters = ''
    was_mobile = st.session_state.get('is_mobile', False)
    # st.cache_data.clear()
    st.session_state.clear()
    cc = 0
    maxc = 125
    while 'pangrams' not in st.session_state or len(st.session_state['pangrams'])<1 and cc<maxc:
        st.session_state.clear()
        reset_state(is_hourly_game=cc+1)
        st.session_state['is_mobile'] = was_mobile
        cc+=1
    man_letters = st.session_state['letters']
    return man_letters

# @st.cache_data(persist=True)
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

    if not st.session_state.get('is_mobile', False):
        fsizze = '55'
        sizze = '85'
        bcolor = '#B9B9B9'
        prefix = f'<span style="opacity:95%; color: yellow; background-color: {bcolor}; font-size: {fsizze}px; display: inline-block; width: {sizze}px; height: {sizze}px; border-radius: 80%; text-align: center; line-height: {sizze}px;">'
        bl_prefix = prefix.replace('yellow', 'black')

        letters = [l.upper() for l in letters]
        c1.write('')
        c1.write('')
        c2.markdown(bl_prefix+letters[2]+'</span>', unsafe_allow_html=True)
        c3.write('')
        c3.write('')
        c3.write()

        c1.markdown(bl_prefix+letters[1]+'</span>', unsafe_allow_html=True)
        c3.markdown(bl_prefix+letters[3]+'</span>', unsafe_allow_html=True)
        c2.markdown(prefix+letters[0]+'</span>', unsafe_allow_html=True)

        c1.markdown(bl_prefix+letters[4]+'</span>', unsafe_allow_html=True)
        c3.markdown(bl_prefix+letters[5]+'</span>', unsafe_allow_html=True)
        c2.markdown(bl_prefix+letters[6]+'</span>', unsafe_allow_html=True)
    else:
        letters = [l.upper() for l in letters]
        fsizze = '70'
        sizze = '200'
        prefix = f'<span style="opacity:80%; color: yellow; background-color: #B9B9B9; font-size: {fsizze}px; display: inline-block;">'
        bl_prefix = prefix.replace('yellow', '').replace('#B9B9B9', '')
        c1.markdown(prefix+' '.join(letters[0])+'</span>   ' + bl_prefix+' '.join(letters[1:])+'</span>', unsafe_allow_html=True)


def find_game(man_letters=[], is_hourly_game=0):
    lowercase_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    if is_hourly_game:
        random.seed(on_the_hour_ts()+is_hourly_game)
        letters = random.sample(lowercase_letters, 7)
        # st.warning(letters)
    else:
        lls = list(set(np.random.randint(0, len(lowercase_letters)-1, 7)))

        count = 0
        while len(lls)<7:
            lls += [count % 26]
            lls = list(set(lls))
            count+=1

        letters = list(set([lowercase_letters[x] for x in lls]))

    if man_letters and len([x.lower() for x in man_letters if x.strip()!='' ])==7:
        print(man_letters)
        letters = [x.lower() for x in man_letters if x.strip()!='' ]
        st.sidebar.warning(f'manual override: {" ".join(letters)}')

    words = load_word_list()

    answers = filter_words(words, letters)
    supwords = pangram_words(answers, letters)

    return letters, answers, supwords

def flip_mobile():
    if 'is_mobile' not in st.session_state:
        st.session_state['is_mobile'] = False
    st.session_state['is_mobile'] = not st.session_state['is_mobile']

def reset_state(man_letters=[], is_hourly_game=False):
    if 'in_a_game' not in st.session_state:
        letters, words, pangrams = find_game(man_letters, is_hourly_game)
        st.session_state['in_a_game'] = True
        st.session_state['is_mobile'] = False

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
    man_letters = st.sidebar.text_input('manual override letters:', '')
    man_letters_proc = [x.lower() for x in man_letters.split(' ')]
    if len(set(man_letters_proc)) == 7 and st.session_state['letters'] != man_letters_proc:
        # st.cache_data.clear()
        st.session_state.clear()
        reset_state(man_letters_proc)

    b1, b2 = st.sidebar.columns(2)
    if b1.button('New Pangram'):
        man_letters = ''
        was_mobile = st.session_state.get('is_mobile', False)
        # st.cache_data.clear()
        st.session_state.clear()
        cc = 0
        maxc = 55
        while 'pangrams' not in st.session_state or len(st.session_state['pangrams'])<1 and cc<maxc:
            st.session_state.clear()
            reset_state()
            st.session_state['is_mobile'] = was_mobile
            cc+=1
            # print(st.session_state['pangrams'])
    if b2.button('New Game'):
        man_letters = ''
        was_mobile = st.session_state.get('is_mobile', False)
        # st.cache_data.clear()
        st.session_state.clear()
        reset_state()
        st.session_state['is_mobile'] = was_mobile

    
    st.header('Spelling Bee 🐝')
    reset_state()
    # st.write(st.session_state['letters'])
    guesscol, anscol = st.columns([15, 5])

    # st.sidebar.json(st.session_state, expanded=False)

    guess = guesscol.text_input('guess:', )
    warningbox = guesscol.container()
    warningbox.write('\n')

    guess = guess.lower()
    D1, D2 = st.sidebar.columns(2)
    D1.button('Letter Resize', on_click=flip_mobile)
    if st.session_state.get('is_mobile', False):
        c1, = guesscol.columns(1, gap='large')
        # c1.button('o', on_click=flip_mobile)
        c0, c2, c3 = guesscol.columns(3)
    else:
        c0, c1, c2, c3, _ = guesscol.columns([1,1,1,1, 1], gap='large')
    
    if D2.button('Hourly Game'):
        hourly_letters = load_hourly_letters(on_the_hour_ts())
        # st.cache_data.clear()
        st.session_state.clear()
        reset_state(hourly_letters)

    def redraw_letters():
        draw_letters(st.session_state['letters'], c1, c2, c3)
        
    # draw_letters(st.session_state['letters'], c1, c2, c3)
    redraw_letters()
    # e1,e2,e3 = guesscol.columns([1,1,1])
    # e1.button('delete')
    # guesscol.button('🔄', use_container_width=True, on_click=redraw_letters)
    # e3.button('enter', help='mommy')


    # aw, sw = st.sidebar.columns(2)
    with st.sidebar.expander('available words: ' + str(len(st.session_state['words']))):
        st.json(st.session_state['words'], expanded=True)
    with st.sidebar.expander('pangrams: ' + str(len(st.session_state['pangrams']))):
        st.json(st.session_state['pangrams'], expanded=True)

    if len(st.session_state['words']) < 4:
        warningbox.warning('not many words: '+str(len(st.session_state['words'])))

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
            warningbox.warning('word must include the center letter: "' + st.session_state['letters'][0]+'"')
        elif not is_word:
            non_overlap = set(guess) - set(guess).intersection(st.session_state['letters'])
            if non_overlap:
                warningbox.warning(f'"{guess}" contains excess letters: ' +str(non_overlap))
            else:
                warningbox.warning(f'"{guess}" is not a valid dictionary word')
        elif not not_prev_guess:
            warningbox.warning('you already found this word')

    current_score = st.session_state['score']

    level = 'Beginner'
    if current_score > 100:
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
    elif current_score > 4:
        level = 'Meh'



    anscol.progress(min(current_score, 100), text=level)
    anscol.button('score: ' + str(current_score),
                  disabled=False,
                  help=RULES_STR)
    num_found = len(st.session_state['answers'])
    if num_found:
        word_plural = 'word' if num_found <= 1 else 'words'
        anscol.write(f'You found {num_found} {word_plural}!')
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