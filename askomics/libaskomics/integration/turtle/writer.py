from io import StringIO


def resource2turtle(resource):
    s = StringIO()
    if __debug__:
        write_pretty_resource(resource, s.write)
    else:
        write_resource(resource, s.write)
    return s.getvalue()


def write_resource(resource, write_func):
    subject = resource.id
    it = iter(resource) # iterator over (predicate, objects) tuples

    # Print first subjet predicate pair
    predicate, objects = next(it)
    write_func(subject)
    write_func(' ')
    write_func(predicate)
    write_func(' ')
    if isinstance(objects, TurtleElement):
        write_func(objects)
    else:
        write_func(','.join(objects))

    for predicate, objects in it:
        write_func(';')
        write_func(predicate)
        write_func(' ')
        if isinstance(objects, TurtleElement):
            write_func(objects)
        else:
            write_func(','.join(objects))

    write_func('.')

def write_pretty_resource(resource, write_func):
    def pretty_serialize_objects(objects, newline):
        "Utility function to serialize a series of RDF object"
        objects = iter(objects)
        write_func(next(objects))

        for object in objects:
            write_func(newline)
            write_func(object)

    subject = resource.id

    # newline sequence
    newline = '\n' + ' ' * (len(subject) - 1)
    it = iter(resource)  # iterator over (predicate, objects) tuples

    # Print first subjet predicate pair
    predicate, objects = next(it)
    write_func(subject)
    write_func(' ')
    write_func(predicate)
    write_func(' ')
    if type(objects) is set:
        pretty_serialize_objects(objects,
                                    newline + ' ' * len(predicate) + ' , ')
    else:
        write_func(objects)

    newpred = newline + '; ' # line indentation for new predicate
    for predicate, objects in it:
        write_func(newpred)
        write_func(predicate)
        write_func(' ')
        if type(objects) is set:
            pretty_serialize_objects(objects,
                                        newline + ' ' * len(predicate) + ' , ')
        else:
            write_func(objects)

    write_func(' .\n\n')



