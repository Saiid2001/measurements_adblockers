import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--extn', type=str)
if len(sys.argv) < 2:
    parser.print_help(sys.stderr)
    sys.exit(1)
args = parser.parse_args()

f = open('filterlist/exceptionrules.txt', 'r')
accept_ads = f.readlines()
f.close()

path = f"filterlist/{args.extn}/"
dir_list = os.listdir(path)

rules = []
for file in dir_list:
    f = open(path+file, 'r')
    rules.extend(f.readlines())
    f.close()

# strip rules into two parts -> rules_allowed (with the @@), rules_blocked 
rules_allowed = []
rules_blocked = []
for rule in rules:
    if rule.startswith('@@||'):
        domain = rule.split('@@||')[1]
        domain = domain.split('?')[0]       
        domain = domain.split('$')[0]
        domain = domain.split('^')[0]
        domain = domain.split('\n')[0]
        rules_allowed.append(domain)
    elif rule.startswith('||'):
        domain = rule.split('||')[1]
        domain = domain.split('?')[0]       
        domain = domain.split('$')[0]
        domain = domain.split('^')[0]
        domain = domain.split('\n')[0]
        rules_blocked.append(domain)

# strip accept_ads to include only domains
rules_exception = []
for rule in accept_ads:
    if rule.startswith('@@||'):
        domain = rule.split('@@||')[1]
        domain = domain.split('?')[0]
        domain = domain.split('$')[0]        
        domain = domain.split('^')[0]        
        domain = domain.split('\n')[0]        
        rules_exception.append(domain)

count = 0


match_list = []
f = open(f'{args.extn}.log', 'w')
for exception in rules_exception:
    for rule in rules_blocked:
        # match = os.path.commonprefix([exception.split('/')[0], rule.split('/')[0]])
        
        match = exception
        match_doms = match.split('.')
        rule_doms = rule.split('.')
        check = 0
        if len(rule_doms) > 1:
            if (match_doms[0] == rule_doms[0]) and (match_doms[1] == rule_doms[1]):
                check = 1
        if len(rule_doms) > 2 and len(match_doms) > 2:
            if (match_doms[1] == rule_doms[1]) and (match_doms[2] == rule_doms[2]):
                check = 1

        if (check):
            # match = match.split('/')[0]
            match = rule.split('/')[0]
            if match not in match_list:
                if match[-1] == '/':
                    match_list.append(match)
                    match_list.append(match[:-1])
                else:
                    match_list.append(match)
                    # match_list.append(match+'/')
                count += 1
                f.write(f'{match} for {exception}')
                f.write('\n')
            break

f.close()         
print(f'count_exception: {count}')

# f.write(f'Total conflicts: {count}')
# f.close()

# print(f'Total conflicts: {count}')
count = 0
match_list = []
for exception in rules_exception:
    for rule in rules_allowed:
        # match = os.path.commonprefix([exception.split('/')[0], rule.split('/')[0]])
        # print(exception)
        # print(rule)
        match = exception
        match_doms = match.split('.')
        rule_doms = rule.split('.')
        check = 0
        if len(rule_doms) > 1:
            if (match_doms[0] == rule_doms[0]) and (match_doms[1] == rule_doms[1]):
                check = 1
        if len(rule_doms) > 2 and len(match_doms) > 2:
            if (match_doms[1] == rule_doms[1]) and (match_doms[2] == rule_doms[2]):
                check = 1

        if (check):
            # match = match.split('/')[0]
            match = rule.split('/')[0]
            if match not in match_list:
                if match[-1] == '/':
                    match_list.append(match)
                    match_list.append(match[:-1])
                else:
                    match_list.append(match)
                    # match_list.append(match+'/')
                count += 1
            break

print(f'count_allowed: {count}')
