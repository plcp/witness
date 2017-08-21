#!/bin/bash
#
#
# Integration in fuddly as the knowledge component
#

repo="https://github.com/plcp/witness"

# Few utilities
confirm()
{
    echo "$@, do you confirm ? (^D to cancel)"
    if read;
    then return;
    else exit 1;
    fi
}

confirm_run()
{
    confirm "$ « $@ »"
    $@
}

# Sanity checks
if pwd | grep -Evq "fuddly/framework$";
then
    echo "Please cd to fuddly/framework before executing this script."
    exit 1
fi

if echo "${BASH_SOURCE[0]}" | grep -Evq "witness/.fixtures/knowledge.sh$";
then
    echo 'Are you sure of what you are doing ? (type "yes" to confirm) '
    read confirm
    if [ ! "$confirm" = "yes" ];
    then
        return 2> /dev/null > /dev/null
        exit 1
    fi
fi

# Pick fuddly's root
cd ..
fuddly_root="$PWD"
confirm "Fuddly path is \"$fuddly_root\""
kn_root="$fuddly_root/framework/knowledge"

# Retrieve the last commit of the repository
tmp_root="$(mktemp -d)"
git clone --depth 1 $repo $tmp_root 2> /dev/null
cd "$tmp_root"

# Compare the last commit known to the commit retrieved
last_rev="$(cat "$kn_root/.rev" 2> /dev/null)"
if [ "$(git rev-parse --verify HEAD)" = "$last_rev" ];
then
    echo 'Already at the last revision, nothing to update.'
    rm -rf "$tmp_root"
    exit 1
fi

# Update the repository
echo -e "\n\nMissing some commits, updating."

# Cleanup temporary root
cd "$fuddly_root"
rm -rf "$tmp_root"

# Remove the current repository
if [ -d "$kn_root" ];
then
    confirm_run "rm -rf $kn_root"
fi

if [ -d "$fuddly_root/test/unit/knowledge" ];
then
    confirm_run "rm -rf $fuddly_root/test/unit/knowledge"
fi

# Clone a new one
git clone "$repo" "$kn_root"

# Update last revision
cd "$kn_root"
git rev-parse --verify HEAD > .rev-new

# Cleanup unused files
confirm_run "rm $(ls | grep -v witness | xargs)"
rm -rf .git .fixtures

# Move files
mv $PWD/witness/* $PWD/
rmdir "$PWD/witness"
rm .gitignore

# Patch
find -iname "*.py" -exec sed -i 's/\<wit\>/kn/g;s/\<witness\>/framework.knowledge/g' {} \+

# Patcher
find -iname "*.py" -exec sed -i 's/\<boil\>/all/g;' {} \+
find -iname "*.py" -exec sed -i 's/\.\<fuzzy\>/.evidence/g;' {} \+
find -iname "*.py" -exec sed -i "s/ 'fuzzy',/ 'evidence',/g;" {} \+
find -iname "*.py" -exec sed -i "s/test_fuzzy/test_evidence/g;" {} \+
find -iname "*.py" -exec sed -i 's/oracle.new(/oracle.oracle(/g;' {} \+
find -iname "*.py" -exec sed -i 's/refine.data(/refine.refine(/g;' {} \+

# Patchest
sed -i "s/class data(/class refine(/g" "refine.py"
sed -i "s/class label(data/class label(refine/g" "refine.py"
sed -i "s/from test_/from test.unit.knowledge.test_/g" "test_modules/boil.py"
sed -i "s/test_name = 'framework.knowledge.test_modules/test_name = 'test.unit.knowledge/g" "test_modules/__init__.py"

# Patchester
head -n -9 "__init__.py" > "__init__.py.new"
head -n -3 "oracle.py" > "oracle.py.new"
mv -f "__init__.py.new" "__init__.py"
mv -f "oracle.py.new" "oracle.py"

# Patchestest
mv "boil.py" "all.py"
mv "test_modules/boil.py" "test_modules/all.py"

# (sic)
mv "test_modules/test_fuzzy.py" "test_modules/test_evidence.py"
mv "fuzzy.py" "evidence.py"
mv "test_modules" "$fuddly_root/test/unit/knowledge"

# Add tests
test_init="$fuddly_root/test/unit/__init__.py"
if grep -q "knowledge" "$test_init";
then :
else
    echo "" >> "$test_init"
    echo "import test.unit.knowledge" >> "$test_init"
    echo "from test.unit.knowledge.all import *" >> "$test_init"
fi

# Apply rev
mv -f .rev-new .rev
echo -e "\n\nFinished (results not guaranteed)."
