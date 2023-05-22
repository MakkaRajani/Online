from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def token(username,seconds):
    s=Serializer('#nhy@uh7',seconds)
    return s.dumps({'user':username}).decode('utf-8')

