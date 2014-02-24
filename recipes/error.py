from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template, Context


def final_error(msg, number, request):
    """

    @rtype : HttpResponse
    """
    msg1 = "1. Download the cookbook correctly"
    msg2 = "2. The cookbook is well formed"
    msg3 = "3. The repository could be updated with the cookbook"
    msg4 = "4. Cookbook upload to the chef-server correctly"
    msg5 = "5. Integration test has been passed by the install recipe"
    msg6 = "6. The recipe is uploaded to SDC-catalog"
    msg7 = "7. Finished Testing process"
    template = get_template('progress.html')
    if number == 0:
        c = Context({"msg1": msg1, "msg2": msg2, "msg3": msg3, "msg4": msg4,
                     "msg5": msg5, "msg6": msg6, "msg7": msg7,
                     "ok": "Well Done", "value": 100, "frac": "7/7"})
    elif number == 1:
        c = Context({"err": msg, "value": 12.5, "frac": "0/7"})
    elif number == 2:
        c = Context({"msg1": msg1, "err": msg, "value": 25, "frac": "1/7"})
    elif number == 3:
        c = Context({"msg1": msg1, "msg2": msg2, "err": msg, "value": 37.5,
                     "frac": "2/7"})
    elif number == 4:
        c = Context(
            {"msg1": msg1, "msg2": msg2, "msg3": msg3, "err": msg, "value": 50,
             "frac": "3/7"})
    elif number == 5:
        c = Context({"msg1": msg1, "msg2": msg2, "msg3": msg3, "msg4": msg4,
                     "err": msg, "value": 62.5, "frac": "4/7"})
    elif number == 6:
        c = Context({"msg1": msg1, "msg2": msg2, "msg3": msg3, "msg4": msg4,
                     "msg5": msg5, "err": msg, "value": 75, "frac": "5/7"})
    elif number == 7:
        c = Context({"msg1": msg1, "msg2": msg2, "msg3": msg3, "msg4": msg4,
                     "msg5": msg5, "msg6": msg6, "err": msg, "value": 87.5,
                     "frac": "6/7"})
    else:
        c = Context({"err": msg, "value": 0})
    return HttpResponse(template.render(RequestContext(request, c)))
