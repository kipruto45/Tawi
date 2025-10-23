from django.urls import get_resolver
resolver = get_resolver(None)
names = [n for n in resolver.reverse_dict.keys() if isinstance(n, str) and 'register' in n]
print(names)
# print some other helpful names
print('login in names?', 'login' in [n for n in resolver.reverse_dict.keys() if isinstance(n,str)])
print('guest_dashboard in names?', 'guest_dashboard' in [n for n in resolver.reverse_dict.keys() if isinstance(n,str)])
