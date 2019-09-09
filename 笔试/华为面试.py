'''
1、字符串回文分割 ‘abccb'  ['a','b','c','c','d'] ['a','b','cc','d'] ['a','bccb']
2、字符串中最大的回文长度 'abccb' 'bccb' 4
'''


class Solution:
    def partition(self, s):
        if s == '':
            return []
        e = []
        if s == s[::-1]:
            e.append([s])
        for i in range(len(s)):
            if s[:i+1] == s[i::-1]:
                p = self.partition(s[i+1:])
                for c in p:
                    if c != []:
                        e.append([s[:i+1]]+c)
        return e


class Solution2:
    def longestPalindrome(self, s):
        res = ""
        for i in range(len(s)):
            tmp = self.helper(s, i, i)
            #odd case like aba
            if (len(tmp) > len(res)):
                res = tmp

            tmp = self.helper(s, i, i+1)
            #even case like abba
            if (len(tmp) > len(res)):
                res = tmp
        return res
    # get the longest palindrome, 1, r are the middle indexes
    # from inner to outer

    def helper(self, s, l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return s[l+1:r]


# s = Solution()
s = Solution2()
text = 'abccb'
# result = s.partition(str)
# print(result)
result = s.longestPalindrome(text)
print(result)
print(len(result))

