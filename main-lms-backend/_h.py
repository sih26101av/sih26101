lines = open('routers/chatbot.py', encoding='utf-8').readlines()
out = []
keywords = ['navigation_login', 'user_identity', 'profile_stats', 'skill_gaps', 'ctx ==']
for i, l in enumerate(lines):
    if any(k in l for k in keywords):
        out.append(f'{i+1}: {l.rstrip()}')
open('_handlers2.txt', 'w').write('\n'.join(out))
print('done')
