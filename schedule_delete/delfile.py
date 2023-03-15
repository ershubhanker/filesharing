from shareit.models import File



def deletefiles():
    print("Hello world")
    delt = File.objects.all()
    delt.delete()
    return ( 'delete.html')