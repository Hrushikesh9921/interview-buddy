"""
Challenge template seed data.
Contains 15 professional coding interview challenges.
"""
from config.constants import ChallengeCategory, ChallengeDifficulty


CHALLENGE_TEMPLATES = [
    # ==================== ALGORITHMS ====================
    {
        "title": "Two Sum",
        "description": "Find two numbers in an array that add up to a target sum",
        "category": ChallengeCategory.ALGORITHMS,
        "difficulty": ChallengeDifficulty.EASY,
        "instructions": """### Problem Statement
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

### Constraints
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists

### Examples

**Example 1:**
```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

**Example 2:**
```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

**Example 3:**
```
Input: nums = [3,3], target = 6
Output: [0,1]
```""",
        "starter_code": """def two_sum(nums, target):
    \"\"\"
    Find two numbers that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
        
    Returns:
        List of two indices
    \"\"\"
    # Your code here
    pass


# Test cases
print(two_sum([2, 7, 11, 15], 9))  # Expected: [0, 1]
print(two_sum([3, 2, 4], 6))  # Expected: [1, 2]
print(two_sum([3, 3], 6))  # Expected: [0, 1]""",
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "output": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "output": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "output": [0, 1]}
        ],
        "tags": ["array", "hash-table", "two-pointers"],
        "estimated_duration": 900,  # 15 minutes
        "metadata": {
            "hints": [
                "Think about using a hash map to store numbers you've seen",
                "A one-pass solution is possible",
                "For each number, check if (target - number) exists in your hash map"
            ],
            "related_concepts": ["Hash Tables", "Array Traversal", "Complement Search"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft", "Apple"]
        }
    },
    
    {
        "title": "Binary Search",
        "description": "Implement binary search to find a target value in a sorted array",
        "category": ChallengeCategory.ALGORITHMS,
        "difficulty": ChallengeDifficulty.EASY,
        "instructions": """### Problem Statement
Given a sorted array of integers `nums` and an integer `target`, write a function to search `target` in `nums`. If `target` exists, return its index. Otherwise, return -1.

You must write an algorithm with O(log n) runtime complexity.

### Constraints
- 1 <= nums.length <= 10^4
- -10^4 <= nums[i], target <= 10^4
- All integers in nums are unique
- nums is sorted in ascending order

### Examples

**Example 1:**
```
Input: nums = [-1,0,3,5,9,12], target = 9
Output: 4
Explanation: 9 exists in nums and its index is 4
```

**Example 2:**
```
Input: nums = [-1,0,3,5,9,12], target = 2
Output: -1
Explanation: 2 does not exist in nums so return -1
```""",
        "starter_code": """def binary_search(nums, target):
    \"\"\"
    Perform binary search on sorted array.
    
    Args:
        nums: Sorted list of integers
        target: Target value to find
        
    Returns:
        Index of target or -1 if not found
    \"\"\"
    # Your code here
    pass


# Test cases
print(binary_search([-1, 0, 3, 5, 9, 12], 9))  # Expected: 4
print(binary_search([-1, 0, 3, 5, 9, 12], 2))  # Expected: -1""",
        "test_cases": [
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "output": 4},
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "output": -1}
        ],
        "tags": ["array", "binary-search", "divide-and-conquer"],
        "estimated_duration": 600,  # 10 minutes
        "metadata": {
            "hints": [
                "Start with left and right pointers at the array boundaries",
                "Calculate middle index and compare with target",
                "Adjust left or right pointer based on comparison"
            ],
            "related_concepts": ["Binary Search", "Divide and Conquer", "Array Indexing"],
            "companies": ["Google", "Amazon", "Microsoft"]
        }
    },
    
    {
        "title": "Merge Sorted Arrays",
        "description": "Merge two sorted arrays into one sorted array",
        "category": ChallengeCategory.ALGORITHMS,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
You are given two integer arrays `nums1` and `nums2`, sorted in non-decreasing order, and two integers `m` and `n`, representing the number of elements in `nums1` and `nums2` respectively.

Merge `nums1` and `nums2` into a single array sorted in non-decreasing order.

The final sorted array should not be returned by the function, but instead be stored inside the array `nums1`. To accommodate this, `nums1` has a length of `m + n`, where the first `m` elements denote the elements that should be merged, and the last `n` elements are set to 0 and should be ignored. `nums2` has a length of `n`.

### Constraints
- nums1.length == m + n
- nums2.length == n
- 0 <= m, n <= 200
- 1 <= m + n <= 200
- -10^9 <= nums1[i], nums2[j] <= 10^9

### Example

```
Input: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
Output: [1,2,2,3,5,6]
Explanation: Arrays being merged are [1,2,3] and [2,5,6].
Result is [1,2,2,3,5,6].
```""",
        "starter_code": """def merge(nums1, m, nums2, n):
    \"\"\"
    Merge nums2 into nums1 as one sorted array.
    Modifies nums1 in-place.
    
    Args:
        nums1: First sorted array with extra space
        m: Number of elements in nums1
        nums2: Second sorted array
        n: Number of elements in nums2
    \"\"\"
    # Your code here
    pass


# Test case
nums1 = [1, 2, 3, 0, 0, 0]
merge(nums1, 3, [2, 5, 6], 3)
print(nums1)  # Expected: [1, 2, 2, 3, 5, 6]""",
        "test_cases": [
            {
                "input": {"nums1": [1, 2, 3, 0, 0, 0], "m": 3, "nums2": [2, 5, 6], "n": 3},
                "output": [1, 2, 2, 3, 5, 6]
            }
        ],
        "tags": ["array", "two-pointers", "sorting", "merge"],
        "estimated_duration": 1200,  # 20 minutes
        "metadata": {
            "hints": [
                "Try merging from the end of nums1 backwards",
                "Use three pointers: one for current position in merged array, one for end of nums1, one for end of nums2",
                "This avoids having to shift elements"
            ],
            "related_concepts": ["Two Pointers", "Array Manipulation", "Merge Sort"],
            "companies": ["Amazon", "Microsoft", "Facebook"]
        }
    },
    
    {
        "title": "Longest Palindromic Substring",
        "description": "Find the longest palindromic substring in a given string",
        "category": ChallengeCategory.ALGORITHMS,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
Given a string `s`, return the longest palindromic substring in `s`.

A palindrome is a string that reads the same backward as forward.

### Constraints
- 1 <= s.length <= 1000
- s consist of only digits and English letters

### Examples

**Example 1:**
```
Input: s = "babad"
Output: "bab" or "aba"
Explanation: Both are valid answers.
```

**Example 2:**
```
Input: s = "cbbd"
Output: "bb"
```""",
        "starter_code": """def longest_palindrome(s):
    \"\"\"
    Find the longest palindromic substring.
    
    Args:
        s: Input string
        
    Returns:
        Longest palindromic substring
    \"\"\"
    # Your code here
    pass


# Test cases
print(longest_palindrome("babad"))  # Expected: "bab" or "aba"
print(longest_palindrome("cbbd"))  # Expected: "bb"
""",
        "test_cases": [
            {"input": {"s": "babad"}, "output": "bab"},  # or "aba"
            {"input": {"s": "cbbd"}, "output": "bb"}
        ],
        "tags": ["string", "dynamic-programming", "palindrome"],
        "estimated_duration": 1800,  # 30 minutes
        "metadata": {
            "hints": [
                "A palindrome can be expanded from its center",
                "There are 2n-1 centers (n characters and n-1 spaces between them)",
                "Expand around each center and track the longest palindrome found"
            ],
            "related_concepts": ["String Manipulation", "Two Pointers", "Expand Around Center"],
            "companies": ["Amazon", "Microsoft", "Facebook", "Google"]
        }
    },
    
    {
        "title": "Merge K Sorted Lists",
        "description": "Merge K sorted linked lists into one sorted list",
        "category": ChallengeCategory.ALGORITHMS,
        "difficulty": ChallengeDifficulty.HARD,
        "instructions": """### Problem Statement
You are given an array of `k` linked-lists `lists`, each linked-list is sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.

### Constraints
- k == lists.length
- 0 <= k <= 10^4
- 0 <= lists[i].length <= 500
- -10^4 <= lists[i][j] <= 10^4
- lists[i] is sorted in ascending order

### Example

```
Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
Merging them into one sorted list:
1->1->2->3->4->4->5->6
```""",
        "starter_code": """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_k_lists(lists):
    \"\"\"
    Merge K sorted linked lists.
    
    Args:
        lists: List of ListNode heads
        
    Returns:
        Head of merged sorted list
    \"\"\"
    # Your code here
    pass""",
        "test_cases": [
            {"input": {"lists": [[1, 4, 5], [1, 3, 4], [2, 6]]}, "output": [1, 1, 2, 3, 4, 4, 5, 6]}
        ],
        "tags": ["linked-list", "divide-and-conquer", "heap", "merge"],
        "estimated_duration": 2400,  # 40 minutes
        "metadata": {
            "hints": [
                "Use a min-heap to efficiently get the smallest element among all lists",
                "Alternatively, merge lists pair by pair (divide and conquer)",
                "Time complexity should be O(N log k) where N is total nodes and k is number of lists"
            ],
            "related_concepts": ["Heap/Priority Queue", "Divide and Conquer", "Linked Lists"],
            "companies": ["Amazon", "Google", "Microsoft", "Facebook"]
        }
    },
    
    # ==================== DATA STRUCTURES ====================
    {
        "title": "Implement Stack",
        "description": "Implement a stack data structure with push, pop, and top operations",
        "category": ChallengeCategory.DATA_STRUCTURES,
        "difficulty": ChallengeDifficulty.EASY,
        "instructions": """### Problem Statement
Implement a last-in-first-out (LIFO) stack using only two queues. The implemented stack should support all the functions of a normal stack (`push`, `top`, `pop`, and `empty`).

Implement the `MyStack` class:
- `push(x)` Pushes element x to the top of the stack.
- `pop()` Removes the element on the top of the stack and returns it.
- `top()` Returns the element on the top of the stack.
- `empty()` Returns true if the stack is empty, false otherwise.

### Constraints
- 1 <= x <= 9
- At most 100 calls will be made to push, pop, top, and empty
- All calls to pop and top are valid

### Example

```
Input
["MyStack", "push", "push", "top", "pop", "empty"]
[[], [1], [2], [], [], []]

Output
[null, null, null, 2, 2, false]

Explanation
MyStack myStack = new MyStack();
myStack.push(1);
myStack.push(2);
myStack.top(); // return 2
myStack.pop(); // return 2
myStack.empty(); // return False
```""",
        "starter_code": """class MyStack:
    def __init__(self):
        \"\"\"Initialize the stack.\"\"\"
        pass
    
    def push(self, x):
        \"\"\"Push element x to the top of the stack.\"\"\"
        pass
    
    def pop(self):
        \"\"\"Remove and return the top element.\"\"\"
        pass
    
    def top(self):
        \"\"\"Get the top element.\"\"\"
        pass
    
    def empty(self):
        \"\"\"Return True if stack is empty.\"\"\"
        pass


# Test
stack = MyStack()
stack.push(1)
stack.push(2)
print(stack.top())  # Expected: 2
print(stack.pop())  # Expected: 2
print(stack.empty())  # Expected: False""",
        "test_cases": [
            {"operations": ["MyStack", "push", "push", "top", "pop", "empty"],
             "args": [[], [1], [2], [], [], []],
             "output": [None, None, None, 2, 2, False]}
        ],
        "tags": ["stack", "design", "queue"],
        "estimated_duration": 900,  # 15 minutes
        "metadata": {
            "hints": [
                "The simplest way is to use a list",
                "push() appends to the end",
                "pop() removes from the end",
                "top() returns the last element without removing it"
            ],
            "related_concepts": ["Stack", "LIFO", "Data Structure Design"],
            "companies": ["Amazon", "Microsoft", "Google"]
        }
    },
    
    {
        "title": "Implement Queue using Stacks",
        "description": "Implement a FIFO queue using only two stacks",
        "category": ChallengeCategory.DATA_STRUCTURES,
        "difficulty": ChallengeDifficulty.EASY,
        "instructions": """### Problem Statement
Implement a first in first out (FIFO) queue using only two stacks. The implemented queue should support all the functions of a normal queue (`push`, `peek`, `pop`, and `empty`).

Implement the `MyQueue` class:
- `push(x)` Pushes element x to the back of queue.
- `pop()` Removes the element from the front of queue and returns it.
- `peek()` Returns the element at the front of queue.
- `empty()` Returns true if the queue is empty, false otherwise.

### Example

```
Input
["MyQueue", "push", "push", "peek", "pop", "empty"]
[[], [1], [2], [], [], []]

Output
[null, null, null, 1, 1, false]
```""",
        "starter_code": """class MyQueue:
    def __init__(self):
        \"\"\"Initialize the queue with two stacks.\"\"\"
        pass
    
    def push(self, x):
        \"\"\"Push element to the back of queue.\"\"\"
        pass
    
    def pop(self):
        \"\"\"Remove and return front element.\"\"\"
        pass
    
    def peek(self):
        \"\"\"Get the front element.\"\"\"
        pass
    
    def empty(self):
        \"\"\"Return True if queue is empty.\"\"\"
        pass


# Test
queue = MyQueue()
queue.push(1)
queue.push(2)
print(queue.peek())  # Expected: 1
print(queue.pop())  # Expected: 1
print(queue.empty())  # Expected: False""",
        "test_cases": [
            {"operations": ["MyQueue", "push", "push", "peek", "pop", "empty"],
             "args": [[], [1], [2], [], [], []],
             "output": [None, None, None, 1, 1, False]}
        ],
        "tags": ["queue", "stack", "design"],
        "estimated_duration": 1200,  # 20 minutes
        "metadata": {
            "hints": [
                "Use one stack for input, one for output",
                "When popping, if output stack is empty, transfer all from input stack",
                "This gives amortized O(1) for all operations"
            ],
            "related_concepts": ["Queue", "Stack", "Amortized Analysis"],
            "companies": ["Amazon", "Microsoft", "Bloomberg"]
        }
    },
    
    {
        "title": "LRU Cache",
        "description": "Design and implement a Least Recently Used (LRU) cache",
        "category": ChallengeCategory.DATA_STRUCTURES,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the `LRUCache` class:
- `LRUCache(capacity)` Initialize the LRU cache with positive size capacity.
- `get(key)` Return the value of the key if it exists, otherwise return -1.
- `put(key, value)` Update the value of the key if it exists. Otherwise, add the key-value pair. If the number of keys exceeds the capacity, evict the least recently used key.

The functions `get` and `put` must each run in O(1) average time complexity.

### Example

```
Input
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]

Output
[null, null, null, 1, null, -1, null, -1, 3, 4]

Explanation
LRUCache lRUCache = new LRUCache(2);
lRUCache.put(1, 1);
lRUCache.put(2, 2);
lRUCache.get(1);    // return 1
lRUCache.put(3, 3); // evicts key 2
lRUCache.get(2);    // returns -1 (not found)
lRUCache.put(4, 4); // evicts key 1
lRUCache.get(1);    // return -1 (not found)
lRUCache.get(3);    // return 3
lRUCache.get(4);    // return 4
```""",
        "starter_code": """class LRUCache:
    def __init__(self, capacity):
        \"\"\"Initialize LRU cache with capacity.\"\"\"
        pass
    
    def get(self, key):
        \"\"\"Get value for key, return -1 if not found.\"\"\"
        pass
    
    def put(self, key, value):
        \"\"\"Set key-value pair, evict LRU if needed.\"\"\"
        pass


# Test
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))  # Expected: 1
cache.put(3, 3)  # evicts key 2
print(cache.get(2))  # Expected: -1""",
        "test_cases": [
            {
                "operations": ["LRUCache", "put", "put", "get", "put", "get"],
                "args": [[2], [1, 1], [2, 2], [1], [3, 3], [2]],
                "output": [None, None, None, 1, None, -1]
            }
        ],
        "tags": ["hash-table", "linked-list", "design", "lru"],
        "estimated_duration": 2400,  # 40 minutes
        "metadata": {
            "hints": [
                "Use a hash map for O(1) lookups",
                "Use a doubly linked list to maintain order",
                "Most recently used at head, least at tail",
                "On access, move node to head"
            ],
            "related_concepts": ["Hash Map", "Doubly Linked List", "Cache Design"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft"]
        }
    },
    
    {
        "title": "Binary Search Tree Operations",
        "description": "Implement insert, search, and delete operations for a BST",
        "category": ChallengeCategory.DATA_STRUCTURES,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
Implement the following operations for a Binary Search Tree:
- `insert(val)` Insert a value into the BST
- `search(val)` Search for a value in the BST, return True if found
- `delete(val)` Delete a value from the BST

A binary search tree is a binary tree where for each node:
- All values in the left subtree are less than the node's value
- All values in the right subtree are greater than the node's value

### Example

```
Input:
bst = BST()
bst.insert(5)
bst.insert(3)
bst.insert(7)
bst.search(3)  # True
bst.delete(3)
bst.search(3)  # False
```""",
        "starter_code": """class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        \"\"\"Insert a value into the BST.\"\"\"
        pass
    
    def search(self, val):
        \"\"\"Search for a value, return True if found.\"\"\"
        pass
    
    def delete(self, val):
        \"\"\"Delete a value from the BST.\"\"\"
        pass


# Test
bst = BST()
bst.insert(5)
bst.insert(3)
bst.insert(7)
print(bst.search(3))  # Expected: True
bst.delete(3)
print(bst.search(3))  # Expected: False""",
        "test_cases": [
            {
                "operations": ["insert", "insert", "insert", "search", "delete", "search"],
                "args": [[5], [3], [7], [3], [3], [3]],
                "output": [None, None, None, True, None, False]
            }
        ],
        "tags": ["tree", "binary-search-tree", "recursion"],
        "estimated_duration": 2400,  # 40 minutes
        "metadata": {
            "hints": [
                "Insert: Recursively find the correct position",
                "Search: Compare with current node and go left or right",
                "Delete: Handle three cases: leaf, one child, two children"
            ],
            "related_concepts": ["Binary Search Tree", "Tree Traversal", "Recursion"],
            "companies": ["Amazon", "Microsoft", "Google"]
        }
    },
    
    {
        "title": "Trie (Prefix Tree) Implementation",
        "description": "Implement a Trie data structure for efficient string operations",
        "category": ChallengeCategory.DATA_STRUCTURES,
        "difficulty": ChallengeDifficulty.HARD,
        "instructions": """### Problem Statement
Implement a trie (prefix tree) with `insert`, `search`, and `startsWith` methods.

A trie is a tree data structure used to efficiently store and retrieve keys in a dataset of strings.

Implement the `Trie` class:
- `Trie()` Initializes the trie object.
- `insert(word)` Inserts the string word into the trie.
- `search(word)` Returns true if word is in the trie, false otherwise.
- `startsWith(prefix)` Returns true if there is any word in the trie that starts with prefix.

### Example

```
Input
["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]

Output
[null, null, true, false, true, null, true]
```""",
        "starter_code": """class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    def __init__(self):
        \"\"\"Initialize the trie.\"\"\"
        self.root = TrieNode()
    
    def insert(self, word):
        \"\"\"Insert a word into the trie.\"\"\"
        pass
    
    def search(self, word):
        \"\"\"Return True if word is in trie.\"\"\"
        pass
    
    def starts_with(self, prefix):
        \"\"\"Return True if any word starts with prefix.\"\"\"
        pass


# Test
trie = Trie()
trie.insert("apple")
print(trie.search("apple"))  # Expected: True
print(trie.search("app"))  # Expected: False
print(trie.starts_with("app"))  # Expected: True""",
        "test_cases": [
            {
                "operations": ["Trie", "insert", "search", "search", "startsWith"],
                "args": [[], ["apple"], ["apple"], ["app"], ["app"]],
                "output": [None, None, True, False, True]
            }
        ],
        "tags": ["trie", "tree", "string", "design"],
        "estimated_duration": 2400,  # 40 minutes
        "metadata": {
            "hints": [
                "Each node stores a map of children (character -> TrieNode)",
                "Mark nodes that represent end of a word",
                "Traverse character by character for all operations"
            ],
            "related_concepts": ["Trie", "Tree", "String Matching", "Prefix Search"],
            "companies": ["Google", "Amazon", "Microsoft"]
        }
    },
    
    # ==================== SYSTEM DESIGN ====================
    {
        "title": "Design URL Shortener",
        "description": "Design a URL shortening service like bit.ly",
        "category": ChallengeCategory.SYSTEM_DESIGN,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
Design a URL shortening service (like bit.ly or TinyURL).

Your system should support:
1. `encode(longUrl)` - Convert a long URL to a short URL
2. `decode(shortUrl)` - Convert a short URL back to the original long URL

### Requirements
- Short URLs should be as short as possible
- Each long URL should always map to the same short URL
- Short URLs should be unique
- The system should handle millions of URLs

### Example

```
Input:
longUrl = "https://www.example.com/very/long/url/path"
shortUrl = encode(longUrl)  # Returns: "http://tiny.url/abc123"
decode(shortUrl)  # Returns: "https://www.example.com/very/long/url/path"
```

### Discussion Points
- How would you generate unique short codes?
- How would you handle collisions?
- What data structure would you use for storage?
- How would you scale this system?""",
        "starter_code": """class URLShortener:
    def __init__(self):
        \"\"\"Initialize the URL shortener.\"\"\"
        pass
    
    def encode(self, long_url):
        \"\"\"
        Encode a long URL to a short URL.
        
        Args:
            long_url: The original long URL
            
        Returns:
            Shortened URL
        \"\"\"
        pass
    
    def decode(self, short_url):
        \"\"\"
        Decode a short URL to the original long URL.
        
        Args:
            short_url: The shortened URL
            
        Returns:
            Original long URL
        \"\"\"
        pass


# Test
shortener = URLShortener()
long_url = "https://www.example.com/very/long/url"
short_url = shortener.encode(long_url)
print(f"Short URL: {short_url}")
print(f"Decoded: {shortener.decode(short_url)}")  # Should equal long_url""",
        "test_cases": [
            {
                "operations": ["encode", "decode"],
                "urls": ["https://www.example.com/test", None],
                "expected": "URLs should match after encode/decode cycle"
            }
        ],
        "tags": ["system-design", "hash-table", "encoding"],
        "estimated_duration": 1800,  # 30 minutes
        "metadata": {
            "hints": [
                "Use base62 encoding (a-z, A-Z, 0-9) for compact representation",
                "Consider using a counter with base62 encoding for uniqueness",
                "Store mappings in a hash map (both directions)",
                "For production: Use database with indexing"
            ],
            "related_concepts": ["Hash Functions", "Base Conversion", "Distributed Systems"],
            "companies": ["Google", "Facebook", "Amazon", "Twitter"]
        }
    },
    
    {
        "title": "Design Rate Limiter",
        "description": "Design a rate limiting system to control API request rates",
        "category": ChallengeCategory.SYSTEM_DESIGN,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
Design a rate limiter that limits the number of requests a user can make within a time window.

Your system should support:
- `is_allowed(user_id)` - Returns True if the request is allowed, False if rate limit exceeded

### Requirements
- Limit: Maximum 5 requests per minute per user
- Should handle multiple users concurrently
- Should be memory efficient

### Example

```
rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

# User 1 makes requests
rate_limiter.is_allowed("user1")  # True
rate_limiter.is_allowed("user1")  # True
# ... 3 more times ...
rate_limiter.is_allowed("user1")  # True (5th request)
rate_limiter.is_allowed("user1")  # False (exceeded limit)
```

### Discussion Points
- Which rate limiting algorithm would you use? (Token Bucket, Sliding Window, Fixed Window)
- How would you handle distributed systems?
- How would you clean up old timestamps?
- What happens when the system clock changes?""",
        "starter_code": """class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        \"\"\"
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        \"\"\"
        pass
    
    def is_allowed(self, user_id):
        \"\"\"
        Check if request is allowed for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if allowed, False if rate limit exceeded
        \"\"\"
        pass


# Test
limiter = RateLimiter(max_requests=5, window_seconds=60)
for i in range(6):
    allowed = limiter.is_allowed("user1")
    print(f"Request {i+1}: {'Allowed' if allowed else 'Denied'}")""",
        "test_cases": [
            {
                "scenario": "5 requests within window should all succeed",
                "expected": [True, True, True, True, True]
            },
            {
                "scenario": "6th request should fail",
                "expected": False
            }
        ],
        "tags": ["system-design", "rate-limiting", "queue"],
        "estimated_duration": 1800,  # 30 minutes
        "metadata": {
            "hints": [
                "Sliding window: Store timestamps of requests in a deque",
                "Remove timestamps older than window_seconds",
                "If remaining requests < max_requests, allow",
                "Use dict to store per-user deques"
            ],
            "related_concepts": ["Rate Limiting", "Sliding Window", "API Design"],
            "companies": ["Amazon", "Google", "Stripe", "Twitter"]
        }
    },
    
    {
        "title": "Design Chat System",
        "description": "Design a basic real-time chat system architecture",
        "category": ChallengeCategory.SYSTEM_DESIGN,
        "difficulty": ChallengeDifficulty.HARD,
        "instructions": """### Problem Statement
Design a simplified real-time chat system that supports:
- One-on-one messaging
- Message history
- Online/offline status

Your implementation should handle:
- `send_message(from_user, to_user, message)` - Send a message
- `get_messages(user1, user2)` - Get conversation history
- `get_online_status(user_id)` - Check if user is online

### Requirements
- Messages should be delivered in order
- System should handle message persistence
- Users should see message history when they log in
- Handle edge cases (offline users, network issues)

### Example

```
chat = ChatSystem()

# User1 sends message to User2
chat.send_message("user1", "user2", "Hello!")
chat.send_message("user2", "user1", "Hi there!")

# Get conversation
messages = chat.get_messages("user1", "user2")
# Returns: [
#   {"from": "user1", "to": "user2", "message": "Hello!", "timestamp": ...},
#   {"from": "user2", "to": "user1", "message": "Hi there!", "timestamp": ...}
# ]
```

### Discussion Points
- How would you implement real-time delivery (WebSockets, polling)?
- How would you shard/partition the message database?
- How would you handle offline message delivery?
- What about message encryption?""",
        "starter_code": """from datetime import datetime
from collections import defaultdict


class ChatSystem:
    def __init__(self):
        \"\"\"Initialize chat system.\"\"\"
        pass
    
    def send_message(self, from_user, to_user, message):
        \"\"\"
        Send a message from one user to another.
        
        Args:
            from_user: Sender user ID
            to_user: Recipient user ID
            message: Message content
        \"\"\"
        pass
    
    def get_messages(self, user1, user2, limit=50):
        \"\"\"
        Get conversation history between two users.
        
        Args:
            user1: First user ID
            user2: Second user ID
            limit: Maximum messages to return
            
        Returns:
            List of message dictionaries
        \"\"\"
        pass
    
    def set_online_status(self, user_id, is_online):
        \"\"\"Set user's online status.\"\"\"
        pass
    
    def get_online_status(self, user_id):
        \"\"\"Get user's online status.\"\"\"
        pass


# Test
chat = ChatSystem()
chat.set_online_status("user1", True)
chat.send_message("user1", "user2", "Hello!")
messages = chat.get_messages("user1", "user2")
print(messages)""",
        "test_cases": [
            {
                "scenario": "Send and retrieve messages",
                "expected": "Messages returned in chronological order"
            }
        ],
        "tags": ["system-design", "real-time", "messaging"],
        "estimated_duration": 3600,  # 60 minutes
        "metadata": {
            "hints": [
                "Use a list or database to store messages",
                "Create a conversation key by sorting user IDs",
                "Store messages with timestamps",
                "Maintain online/offline status in a dict",
                "For production: Consider message queues, WebSockets"
            ],
            "related_concepts": ["Real-time Systems", "Message Queues", "WebSockets", "Database Sharding"],
            "companies": ["WhatsApp", "Facebook", "Slack", "Discord"]
        }
    },
    
    # ==================== STRING MANIPULATION ====================
    {
        "title": "Valid Anagram",
        "description": "Determine if two strings are anagrams of each other",
        "category": ChallengeCategory.CODING,
        "difficulty": ChallengeDifficulty.EASY,
        "instructions": """### Problem Statement
Given two strings `s` and `t`, return true if `t` is an anagram of `s`, and false otherwise.

An anagram is a word formed by rearranging the letters of a different word, using all the original letters exactly once.

### Constraints
- 1 <= s.length, t.length <= 5 * 10^4
- s and t consist of lowercase English letters

### Examples

**Example 1:**
```
Input: s = "anagram", t = "nagaram"
Output: true
```

**Example 2:**
```
Input: s = "rat", t = "car"
Output: false
```""",
        "starter_code": """def is_anagram(s, t):
    \"\"\"
    Check if two strings are anagrams.
    
    Args:
        s: First string
        t: Second string
        
    Returns:
        True if anagrams, False otherwise
    \"\"\"
    # Your code here
    pass


# Test cases
print(is_anagram("anagram", "nagaram"))  # Expected: True
print(is_anagram("rat", "car"))  # Expected: False""",
        "test_cases": [
            {"input": {"s": "anagram", "t": "nagaram"}, "output": True},
            {"input": {"s": "rat", "t": "car"}, "output": False}
        ],
        "tags": ["string", "hash-table", "sorting"],
        "estimated_duration": 600,  # 10 minutes
        "metadata": {
            "hints": [
                "If lengths differ, can't be anagrams",
                "Count character frequencies in both strings",
                "Compare the frequency maps",
                "Alternative: Sort both strings and compare"
            ],
            "related_concepts": ["Hash Map", "Character Frequency", "String Comparison"],
            "companies": ["Amazon", "Google", "Microsoft"]
        }
    },
    
    {
        "title": "Group Anagrams",
        "description": "Group strings that are anagrams of each other",
        "category": ChallengeCategory.CODING,
        "difficulty": ChallengeDifficulty.MEDIUM,
        "instructions": """### Problem Statement
Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.

### Example

```
Input: strs = ["eat","tea","tan","ate","nat","bat"]
Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
```

### Constraints
- 1 <= strs.length <= 10^4
- 0 <= strs[i].length <= 100
- strs[i] consists of lowercase English letters""",
        "starter_code": """def group_anagrams(strs):
    \"\"\"
    Group anagrams together.
    
    Args:
        strs: List of strings
        
    Returns:
        List of grouped anagrams
    \"\"\"
    # Your code here
    pass


# Test
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
print(group_anagrams(strs))
# Expected: [["bat"], ["nat","tan"], ["ate","eat","tea"]]""",
        "test_cases": [
            {
                "input": {"strs": ["eat", "tea", "tan", "ate", "nat", "bat"]},
                "output": [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]
            }
        ],
        "tags": ["string", "hash-table", "sorting", "grouping"],
        "estimated_duration": 1200,  # 20 minutes
        "metadata": {
            "hints": [
                "Use sorted string as a key in hash map",
                "All anagrams will have same sorted form",
                "Group strings with same key together",
                "Return the values from the hash map"
            ],
            "related_concepts": ["Hash Map", "Grouping", "String Sorting"],
            "companies": ["Amazon", "Facebook", "Google"]
        }
    },
    
    {
        "title": "Minimum Window Substring",
        "description": "Find the minimum window in string S that contains all characters of string T",
        "category": ChallengeCategory.CODING,
        "difficulty": ChallengeDifficulty.HARD,
        "instructions": """### Problem Statement
Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string `""`.

### Constraints
- 1 <= s.length, t.length <= 10^5
- s and t consist of uppercase and lowercase English letters

### Example

**Example 1:**
```
Input: s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
Explanation: The minimum window substring "BANC" includes 'A', 'B', and 'C' from string t.
```

**Example 2:**
```
Input: s = "a", t = "a"
Output: "a"
```

**Example 3:**
```
Input: s = "a", t = "aa"
Output: ""
Explanation: Both 'a's from t must be included in the window.
```""",
        "starter_code": """def min_window(s, t):
    \"\"\"
    Find minimum window substring containing all chars from t.
    
    Args:
        s: Source string
        t: Target string
        
    Returns:
        Minimum window substring or empty string
    \"\"\"
    # Your code here
    pass


# Test cases
print(min_window("ADOBECODEBANC", "ABC"))  # Expected: "BANC"
print(min_window("a", "a"))  # Expected: "a"
print(min_window("a", "aa"))  # Expected: ""  """,
        "test_cases": [
            {"input": {"s": "ADOBECODEBANC", "t": "ABC"}, "output": "BANC"},
            {"input": {"s": "a", "t": "a"}, "output": "a"},
            {"input": {"s": "a", "t": "aa"}, "output": ""}
        ],
        "tags": ["string", "sliding-window", "hash-table", "two-pointers"],
        "estimated_duration": 2400,  # 40 minutes
        "metadata": {
            "hints": [
                "Use sliding window approach with two pointers",
                "Expand window by moving right pointer",
                "Contract window by moving left pointer when valid",
                "Track character frequencies with hash maps",
                "Keep track of minimum window found"
            ],
            "related_concepts": ["Sliding Window", "Two Pointers", "Hash Map", "String Matching"],
            "companies": ["Google", "Facebook", "Amazon", "LinkedIn"]
        }
    }
]


def get_challenge_count_by_category():
    """Get count of challenges by category."""
    from collections import Counter
    categories = [c["category"] for c in CHALLENGE_TEMPLATES]
    return dict(Counter(categories))


def get_challenge_count_by_difficulty():
    """Get count of challenges by difficulty."""
    from collections import Counter
    difficulties = [c["difficulty"] for c in CHALLENGE_TEMPLATES]
    return dict(Counter(difficulties))


if __name__ == "__main__":
    print(f"Total challenges: {len(CHALLENGE_TEMPLATES)}")
    print(f"\nBy category: {get_challenge_count_by_category()}")
    print(f"\nBy difficulty: {get_challenge_count_by_difficulty()}")

