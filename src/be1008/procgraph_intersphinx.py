

def get_known_blocks():
    from sphinx.ext.intersphinx import fetch_inventory #@UnresolvedImport
    
    ''' Returns a map block -> url '''
    
    bases = [
        'http://andreacensi.github.com/be1008/',
        'http://andreacensi.github.com/procgraph/',
        'http://andreacensi.github.com/procgraph_rawseeds/']
    
    result = {}
    for base in bases:
        url = base + '/objects.inv'
        map = fetch_inventory(None, base, url);
        labels = map['std:label']
        for key in labels:
            if key.startswith('block:'):
                block = key[6:]
                url = labels[key][2].split()[0]
                result[block] = url
        
    return result

if __name__ == '__main__':
    block2url = get_known_blocks()
    for block, url in block2url.items():
        print block, url
