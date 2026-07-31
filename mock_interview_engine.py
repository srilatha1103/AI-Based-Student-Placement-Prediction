import re
import random

# ---------------------------------------------------------
# Technical Question Bank (10 Domains)
# ---------------------------------------------------------
TECHNICAL_QUESTION_BANK = {
    'Python': [
        {
            'id': 'py_1',
            'question': 'Explain the difference between deep copy and shallow copy in Python.',
            'keywords': ['shallow', 'deep', 'copy', 'reference', 'object', 'mutable', 'nested', 'deepcopy'],
            'model_answer': 'A shallow copy constructs a new object and inserts references to objects found in the original. A deep copy creates a new object and recursively copies all nested objects inside it.'
        },
        {
            'id': 'py_2',
            'question': 'What are Python decorators and how do they work?',
            'keywords': ['decorator', 'function', 'wrapper', 'arguments', 'higher-order', '@', 'return'],
            'model_answer': 'Decorators in Python are higher-order functions that take another function as an argument and extend its behavior without explicitly modifying it. They use the @decorator syntax.'
        },
        {
            'id': 'py_3',
            'question': 'Explain GIL (Global Interpreter Lock) in Python and its impact on multithreading.',
            'keywords': ['gil', 'global interpreter lock', 'thread', 'cpu', 'mutex', 'multiprocessing', 'bytecode'],
            'model_answer': 'The GIL is a mutex that allows only one thread to execute Python bytecode at a time in CPython. This prevents multi-core CPU parallelism for CPU-bound threads.'
        },
        {
            'id': 'py_4',
            'question': 'What is the difference between list, tuple, set, and dictionary in Python?',
            'keywords': ['list', 'tuple', 'set', 'dictionary', 'mutable', 'immutable', 'ordered', 'key-value', 'unique'],
            'model_answer': 'Lists are ordered, mutable collections. Tuples are ordered, immutable collections. Sets are unordered, unique elements. Dictionaries store key-value pairs.'
        }
    ],
    'Java': [
        {
            'id': 'java_1',
            'question': 'Explain the four OOP concepts (Object-Oriented Programming) in Java with examples.',
            'keywords': ['encapsulation', 'inheritance', 'polymorphism', 'abstraction', 'class', 'object'],
            'model_answer': 'The 4 pillars of OOP are Encapsulation (data hiding), Inheritance (code reuse), Polymorphism (overloading/overriding), and Abstraction (hiding implementation details via interfaces/abstract classes).'
        },
        {
            'id': 'java_2',
            'question': 'What is the difference between JVM, JRE, and JDK?',
            'keywords': ['jvm', 'jre', 'jdk', 'virtual machine', 'runtime environment', 'development kit', 'bytecode'],
            'model_answer': 'JDK is the development kit containing tools and JRE. JRE is the runtime environment containing JVM and libraries. JVM is the engine that executes Java bytecode.'
        },
        {
            'id': 'java_3',
            'question': 'Explain Garbage Collection in Java and how the Heap memory is divided.',
            'keywords': ['garbage collection', 'gc', 'heap', 'young generation', 'old generation', 'eden', 'survivor'],
            'model_answer': 'Garbage collection automatically frees unreferenced heap memory. The Java heap is divided into Young Generation (Eden & Survivor spaces), Old/Tenured Generation, and Metaspace.'
        }
    ],
    'C++': [
        {
            'id': 'cpp_1',
            'question': 'Explain the difference between pointers and references in C++.',
            'keywords': ['pointer', 'reference', 'memory address', 'null', 'reassign', 'dereference', '&', '*'],
            'model_answer': 'Pointers store memory addresses and can be NULL or reassigned. References are aliases for existing variables, cannot be NULL, and cannot be reassigned once initialized.'
        },
        {
            'id': 'cpp_2',
            'question': 'What are Virtual Functions and VTABLE in C++?',
            'keywords': ['virtual', 'vtable', 'vptr', 'polymorphism', 'runtime', 'override', 'base class'],
            'model_answer': 'Virtual functions enable runtime polymorphism. VTABLE is a static table of function pointers created for classes with virtual functions, resolved via a hidden VPTR pointer.'
        }
    ],
    'Web Development': [
        {
            'id': 'web_1',
            'question': 'Explain the critical rendering path in browser web development.',
            'keywords': ['dom', 'cssom', 'render tree', 'layout', 'paint', 'reflow', 'repaint', 'parsing'],
            'model_answer': 'The critical rendering path involves parsing HTML into the DOM, parsing CSS into CSSOM, combining them into a Render Tree, calculating Layout (reflow), and Painting pixels onto the screen.'
        },
        {
            'id': 'web_2',
            'question': 'What is the difference between SessionStorage, LocalStorage, and Cookies?',
            'keywords': ['localstorage', 'sessionstorage', 'cookies', 'expiry', 'capacity', 'http', 'domain'],
            'model_answer': 'LocalStorage persists until cleared (5-10MB). SessionStorage lasts for the browser tab session. Cookies (4KB) expire based on headers and are sent with every HTTP request.'
        }
    ],
    'Full Stack Development': [
        {
            'id': 'fs_1',
            'question': 'How does REST API architecture work, and what are key HTTP status codes?',
            'keywords': ['rest', 'stateless', 'http', 'get', 'post', 'put', 'delete', '200', '404', '500', 'json'],
            'model_answer': 'REST APIs use stateless Client-Server HTTP requests. Standard methods are GET, POST, PUT, DELETE. Status codes include 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Server Error.'
        },
        {
            'id': 'fs_2',
            'question': 'Explain JWT (JSON Web Token) authentication flow in full stack apps.',
            'keywords': ['jwt', 'token', 'header', 'payload', 'signature', 'auth', 'bearer', 'stateless'],
            'model_answer': 'JWT authentication signs a token containing Header, Payload, and Signature. The client stores it and sends it in the Authorization Bearer header for stateless verification.'
        }
    ],
    'SQL': [
        {
            'id': 'sql_1',
            'question': 'Explain the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN.',
            'keywords': ['inner join', 'left join', 'right join', 'full join', 'null', 'matching', 'rows', 'table'],
            'model_answer': 'INNER JOIN returns matching rows in both tables. LEFT JOIN returns all rows from left table and matched rows from right. RIGHT JOIN returns all right rows. FULL JOIN returns all rows from both tables.'
        },
        {
            'id': 'sql_2',
            'question': 'What are ACID properties in database transactions?',
            'keywords': ['atomicity', 'consistency', 'isolation', 'durability', 'acid', 'transaction', 'commit', 'rollback'],
            'model_answer': 'ACID stands for Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions don\'t interfere), and Durability (committed data persists permanently).'
        }
    ],
    'AI/ML': [
        {
            'id': 'aiml_1',
            'question': 'Explain Overfitting vs Underfitting in Machine Learning and how to prevent them.',
            'keywords': ['overfitting', 'underfitting', 'bias', 'variance', 'regularization', 'cross-validation', 'dropout'],
            'model_answer': 'Overfitting occurs when a model learns noise in training data (high variance). Underfitting happens when a model is too simple (high bias). Prevent overfitting using regularization, cross-validation, and dropout.'
        },
        {
            'id': 'aiml_2',
            'question': 'What is the difference between Supervised, Unsupervised, and Reinforcement Learning?',
            'keywords': ['supervised', 'unsupervised', 'reinforcement', 'labeled', 'unlabeled', 'reward', 'clustering', 'classification'],
            'model_answer': 'Supervised learning uses labeled training data. Unsupervised learning finds patterns in unlabeled data (e.g. clustering). Reinforcement learning trains agents via rewards and penalties.'
        }
    ],
    'Data Structures': [
        {
            'id': 'dsa_1',
            'question': 'Explain the difference between Array and LinkedList in terms of memory and time complexity.',
            'keywords': ['array', 'linkedlist', 'memory', 'pointer', 'contiguous', 'indexing', 'insertion', 'O(1)', 'O(n)'],
            'model_answer': 'Arrays use contiguous memory with O(1) random index access but O(N) insertion. LinkedLists use non-contiguous node pointers with O(N) access but O(1) pointer insertion.'
        },
        {
            'id': 'dsa_2',
            'question': 'What is Binary Search Tree (BST) and what is its worst-case time complexity?',
            'keywords': ['bst', 'binary search tree', 'left', 'right', 'log n', 'skewed', 'O(n)', 'O(log n)'],
            'model_answer': 'A BST is a node tree where left child < parent < right child. Search time complexity is O(log N) for balanced trees, but degrades to O(N) for skewed unbalanced trees.'
        }
    ],
    'Operating Systems': [
        {
            'id': 'os_1',
            'question': 'Explain Deadlock, its four necessary conditions, and prevention strategies.',
            'keywords': ['deadlock', 'mutual exclusion', 'hold and wait', 'no preemption', 'circular wait', 'banker'],
            'model_answer': 'Deadlock occurs when processes are blocked waiting for each other\'s resources. The 4 conditions are Mutual Exclusion, Hold & Wait, No Preemption, and Circular Wait. Prevent by breaking any one condition or using Banker\'s algorithm.'
        },
        {
            'id': 'os_2',
            'question': 'What is Paging and Virtual Memory in Operating Systems?',
            'keywords': ['paging', 'virtual memory', 'page fault', 'frame', 'page table', 'mmu', 'address space'],
            'model_answer': 'Virtual Memory allows execution of processes larger than physical RAM. Paging divides virtual memory into fixed-size Pages mapped to physical Frames via a Page Table.'
        }
    ],
    'Computer Networks': [
        {
            'id': 'cn_1',
            'question': 'Explain the 7 layers of the OSI model.',
            'keywords': ['physical', 'data link', 'network', 'transport', 'session', 'presentation', 'application', 'osi'],
            'model_answer': 'The 7 OSI layers are: 1. Physical, 2. Data Link, 3. Network (IP), 4. Transport (TCP/UDP), 5. Session, 6. Presentation, 7. Application (HTTP/FTP).'
        },
        {
            'id': 'cn_2',
            'question': 'Explain the 3-Way Handshake process in TCP connection establishment.',
            'keywords': ['tcp', 'syn', 'syn-ack', 'ack', 'handshake', 'connection', 'sequence number'],
            'model_answer': 'TCP 3-Way Handshake establishes a connection: 1. Client sends SYN. 2. Server responds with SYN-ACK. 3. Client responds with ACK to confirm.'
        }
    ]
}

# ---------------------------------------------------------
# HR Question Bank
# ---------------------------------------------------------
HR_QUESTION_BANK = [
    {
        'id': 'hr_1',
        'question': 'Tell me about yourself, your background, and your career aspirations.',
        'keywords': ['education', 'projects', 'skills', 'passion', 'experience', 'growth', 'aspire', 'role'],
        'model_answer': 'Highlight your academic degree, key projects/internships, technical strengths, and enthusiasm for continuous learning and contributing to company goals.'
    },
    {
        'id': 'hr_2',
        'question': 'Why should we hire you for this placement role?',
        'keywords': ['skills', 'align', 'value', 'fit', 'problem-solving', 'dedicated', 'team', 'results'],
        'model_answer': 'Connect your technical skill set, academic achievements, and problem-solving mindset directly with the job requirements and corporate values.'
    },
    {
        'id': 'hr_3',
        'question': 'What are your greatest technical strengths and areas for improvement?',
        'keywords': ['strength', 'weakness', 'learning', 'improve', 'adaptability', 'effort', 'growth'],
        'model_answer': 'State a relevant technical strength backed by project evidence, and mention a genuine area of improvement that you are actively working to enhance.'
    },
    {
        'id': 'hr_4',
        'question': 'Describe a difficult challenge or project obstacle you faced and how you overcame it.',
        'keywords': ['challenge', 'obstacle', 'solution', 'action', 'result', 'learned', 'collaboration'],
        'model_answer': 'Use the STAR method (Situation, Task, Action, Result) to explain a real project bottleneck, the steps you took to debug it, and the successful outcome.'
    },
    {
        'id': 'hr_5',
        'question': 'Where do you see yourself professionally five years from now?',
        'keywords': ['5 years', 'lead', 'architect', 'growth', 'mastery', 'responsibility', 'impact'],
        'model_answer': 'Express your vision to grow into a senior technical engineer or team leader, mastering full-stack architecture and driving key product innovations.'
    }
]

# ---------------------------------------------------------
# Aptitude Question Bank (Quantitative, Logical, Verbal)
# ---------------------------------------------------------
APTITUDE_QUESTION_BANK = [
    {
        'id': 'apt_1',
        'category': 'Quantitative Aptitude',
        'question': 'A train running at a speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train in meters?',
        'options': ['120 meters', '150 meters', '180 meters', '324 meters'],
        'correct_index': 1,
        'explanation': 'Speed in m/s = 60 * (5/18) = 50/3 m/s. Length = Speed * Time = (50/3) * 9 = 150 meters.'
    },
    {
        'id': 'apt_2',
        'category': 'Quantitative Aptitude',
        'question': 'A and B can together complete a piece of work in 12 days. A alone can complete it in 20 days. How many days will B alone take?',
        'options': ['25 days', '30 days', '35 days', '40 days'],
        'correct_index': 1,
        'explanation': '1/B = 1/12 - 1/20 = (5 - 3) / 60 = 2/60 = 1/30. So B alone will take 30 days.'
    },
    {
        'id': 'apt_3',
        'category': 'Logical Reasoning',
        'question': 'Find the next number in the series: 2, 6, 12, 20, 30, ?',
        'options': ['36', '40', '42', '48'],
        'correct_index': 2,
        'explanation': 'Pattern is n*(n+1): 1*2=2, 2*3=6, 3*4=12, 4*5=20, 5*6=30. Next is 6*7 = 42.'
    },
    {
        'id': 'apt_4',
        'category': 'Logical Reasoning',
        'question': 'If CODING is written as DPEJOH in a code language, how is FLASK written in that code?',
        'options': ['GMBTL', 'GMBTK', 'GNCUL', 'ENZRJ'],
        'correct_index': 0,
        'explanation': 'Each letter is shifted by +1: F->G, L->M, A->B, S->T, K->L = GMBTL.'
    },
    {
        'id': 'apt_5',
        'category': 'Verbal Ability',
        'question': 'Choose the word which is most nearly SYNONYMOUS to "METICULOUS":',
        'options': ['Careless', 'Painstaking & Detailed', 'Hasty', 'Vague'],
        'correct_index': 1,
        'explanation': 'Meticulous means taking or showing extreme care about minute details; painstaking.'
    }
]

# ---------------------------------------------------------
# Coding Practice Problems
# ---------------------------------------------------------
CODING_PRACTICE_PROBLEMS = [
    {
        'id': 'code_1',
        'title': 'Two Sum Problem',
        'difficulty': 'Easy',
        'problem_statement': 'Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to target.',
        'sample_input': 'nums = [2, 7, 11, 15], target = 9',
        'sample_output': '[0, 1]',
        'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].',
        'solution_code': '''def twoSum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in lookup:
            return [lookup[diff], i]
        lookup[num] = i
    return []'''
    },
    {
        'id': 'code_2',
        'title': 'Reverse a Linked List',
        'difficulty': 'Medium',
        'problem_statement': 'Given the head of a singly linked list, reverse the list and return its new head node.',
        'sample_input': '1 -> 2 -> 3 -> 4 -> 5 -> NULL',
        'sample_output': '5 -> 4 -> 3 -> 2 -> 1 -> NULL',
        'explanation': 'Iteratively update next pointers using prev, current, and next_node variables in O(N) time and O(1) space.',
        'solution_code': '''def reverseList(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev'''
    },
    {
        'id': 'code_3',
        'title': 'Longest Substring Without Repeating Characters',
        'difficulty': 'Hard',
        'problem_statement': 'Given a string `s`, find the length of the longest substring without repeating characters.',
        'sample_input': 's = "abcabcbb"',
        'sample_output': '3',
        'explanation': 'The answer is "abc", with length 3. Solved using sliding window with hash map storing character indices.',
        'solution_code': '''def lengthOfLongestSubstring(s):
    char_map = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len'''
    }
]

# ---------------------------------------------------------
# Group Discussion Preparation Guides
# ---------------------------------------------------------
GD_PREPARATION_GUIDE = {
    'trending_topics': [
        {'topic': 'Impact of Generative AI & ChatGPT on Engineering Jobs', 'category': 'Technology'},
        {'topic': 'Work From Home vs Hybrid vs Office Return', 'category': 'Corporate Culture'},
        {'topic': 'Cybersecurity Threats in Global FinTech Infrastructure', 'category': 'Security'},
        {'topic': 'Electric Vehicles & Renewable Energy Transition by 2030', 'category': 'Environment'},
        {'topic': 'Data Privacy vs Government Surveillance Regulations', 'category': 'Ethics & Policy'}
    ],
    'gd_strategy_framework': [
        {'step': '1. Initiation', 'tip': 'If confident, start with a crisp definition, quote, or statistical metric. Establish structured direction.'},
        {'step': '2. Building Points', 'tip': 'Use PREP framework: Point, Reason, Example, Point. Support your claims with facts.'},
        {'step': '3. Encouraging & Countering', 'tip': 'Maintain calm body language. Politely acknowledge opposing views ("I agree with your point, but consider...")'},
        {'step': '4. Summarization', 'tip': 'If not initiating, offer to summarize key consensus points at the end.'}
    ]
}

# ---------------------------------------------------------
# Evaluation & AI Feedback Functions
# ---------------------------------------------------------
def generate_interview_questions(category, domain='Python', count=4):
    """Retrieve structured list of questions for session based on category."""
    if category == 'Technical':
        pool = TECHNICAL_QUESTION_BANK.get(domain, TECHNICAL_QUESTION_BANK['Python'])
        return random.sample(pool, min(count, len(pool)))
    elif category == 'HR':
        return random.sample(HR_QUESTION_BANK, min(count, len(HR_QUESTION_BANK)))
    elif category == 'Aptitude':
        return random.sample(APTITUDE_QUESTION_BANK, min(count, len(APTITUDE_QUESTION_BANK)))
    else:
        return TECHNICAL_QUESTION_BANK['Python'][:count]

def get_questions_by_ids(qids, category='Technical', domain='Python'):
    """Rehydrate question objects using question IDs to keep session cookies small."""
    if not qids:
        return generate_interview_questions(category, domain, count=4)

    questions = []
    if category == 'Technical':
        pool = TECHNICAL_QUESTION_BANK.get(domain, TECHNICAL_QUESTION_BANK.get('Python', []))
        q_map = {q['id']: q for q in pool}
        for qid in qids:
            if qid in q_map:
                questions.append(q_map[qid])
    elif category == 'HR':
        q_map = {q['id']: q for q in HR_QUESTION_BANK}
        for qid in qids:
            if qid in q_map:
                questions.append(q_map[qid])
    elif category == 'Aptitude':
        q_map = {q['id']: q for q in APTITUDE_QUESTION_BANK}
        for qid in qids:
            if qid in q_map:
                questions.append(q_map[qid])

    if not questions:
        questions = generate_interview_questions(category, domain, count=4)
    return questions


def evaluate_text_answer(question_obj, user_ans):
    """Evaluate candidate text response using keyword coverage and depth metrics."""
    if not user_ans or len(user_ans.strip()) < 5:
        return {
            'score': 0.0,
            'is_correct': 0,
            'feedback': 'No substantive response provided. Ensure you articulate key technical concepts clearly.'
        }

    user_ans_lower = user_ans.lower()
    keywords = question_obj.get('keywords', [])

    matched_keywords = [k for k in keywords if k.lower() in user_ans_lower]
    keyword_ratio = len(matched_keywords) / len(keywords) if keywords else 0.5

    # Length and depth heuristic
    word_count = len(user_ans.split())
    length_bonus = 0.2 if word_count >= 25 else (0.1 if word_count >= 15 else 0.0)

    score_pct = min(100.0, (keyword_ratio * 80 + length_bonus * 20))
    is_correct = 1 if score_pct >= 60.0 else 0

    if score_pct >= 85:
        fb = f"Excellent answer! Strong explanation covering key concepts: {', '.join(matched_keywords[:4])}."
    elif score_pct >= 60:
        missing = [k for k in keywords if k.lower() not in user_ans_lower]
        fb = f"Good response. To boost your score, consider adding details about: {', '.join(missing[:3])}."
    else:
        missing = [k for k in keywords if k.lower() not in user_ans_lower]
        fb = f"Needs improvement. Missed core technical terms such as: {', '.join(missing[:3])}."

    return {
        'score': round(score_pct, 1),
        'is_correct': is_correct,
        'feedback': fb
    }

def evaluate_aptitude_answer(question_obj, user_selected_index):
    """Evaluate candidate multiple-choice answer."""
    correct_idx = question_obj.get('correct_index', 0)
    is_correct = 1 if int(user_selected_index) == int(correct_idx) else 0
    score = 100.0 if is_correct else 0.0

    options = question_obj.get('options', [])
    correct_text = options[correct_idx] if correct_idx < len(options) else "Correct Option"

    if is_correct:
        fb = f"Correct! {question_obj.get('explanation')}"
    else:
        fb = f"Incorrect. Correct answer is '{correct_text}'. Solution: {question_obj.get('explanation')}"

    return {
        'score': score,
        'is_correct': is_correct,
        'feedback': fb
    }

def evaluate_interview_session(category, domain, answers_input):
    """Process all question submissions, compute total score, strengths, weaknesses, and feedback."""
    total_q = len(answers_input)
    correct_cnt = 0
    total_score_sum = 0.0
    evaluated_answers = []

    strengths = []
    weaknesses = []
    recommended_topics = []

    for item in answers_input:
        q_obj = item['question_obj']
        user_ans = item.get('user_answer', '')

        if category == 'Aptitude':
            try:
                sel_idx = int(user_ans)
            except (ValueError, TypeError):
                sel_idx = -1
            eval_res = evaluate_aptitude_answer(q_obj, sel_idx)
            user_disp = q_obj['options'][sel_idx] if 0 <= sel_idx < len(q_obj['options']) else "None Selected"
            model_disp = q_obj['options'][q_obj['correct_index']]
        else:
            eval_res = evaluate_text_answer(q_obj, user_ans)
            user_disp = user_ans if user_ans else "No Answer"
            model_disp = q_obj.get('model_answer', '')

        if eval_res['is_correct']:
            correct_cnt += 1
            strengths.append(q_obj.get('question', 'Question')[:40] + "...")
        else:
            weaknesses.append(q_obj.get('question', 'Question')[:40] + "...")

        total_score_sum += eval_res['score']

        evaluated_answers.append({
            'question_text': q_obj.get('question'),
            'user_answer': user_disp,
            'model_answer': model_disp,
            'score': eval_res['score'],
            'is_correct': eval_res['is_correct'],
            'feedback': eval_res['feedback']
        })

    avg_score = round(total_score_sum / total_q, 1) if total_q > 0 else 0.0

    if avg_score >= 80:
        overall_fb = f"Outstanding performance in {category} ({domain}) interview! Demonstrates solid conceptual grasp and technical clarity."
        recommended_topics = ['System Architecture', 'Advanced Optimization', 'Mock Live Coding']
    elif avg_score >= 60:
        overall_fb = f"Good performance in {category} ({domain}) interview. With focused revision on missed topics, you will be recruitment-ready."
        recommended_topics = ['DSA Edge Cases', 'Core Syntax Details', 'Quant Speed Drills']
    else:
        overall_fb = f"Requires targeted improvement in {category} ({domain}). Practice fundamental concepts and review sample model answers."
        recommended_topics = ['Core Fundamentals', 'Standard Coding Patterns', 'Aptitude Formulas']

    return {
        'total_questions': total_q,
        'correct_answers': correct_cnt,
        'total_score': avg_score,
        'strengths': strengths if strengths else ['Completed full interview session'],
        'weaknesses': weaknesses if weaknesses else ['No major weaknesses detected'],
        'feedback': overall_fb,
        'recommended_topics': recommended_topics,
        'evaluated_answers': evaluated_answers
    }
