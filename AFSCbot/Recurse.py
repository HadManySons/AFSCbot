'''def checkParentsForMatches(comment):
    workingComment = comment.parent()
    if comment.is_root:
        print("Is root initally")
        return False
    while workingComment.is_root == False:
        formattedParentComment = workingComment.body
        formattedParentComment = formattedParentComment.lower()

        if any(matches in formattedParentComment for matches in triggerWords):
            print("Previous match")
            print(workingComment.id)
            return True
        else:
            print("Checking parent comment")
        workingComment = workingComment.parent()'''

def checkParentsForMatches(comment):
    if comment.is_root:
        print("Is top level comment")
        return False
    else:
        formattedParentComment = comment.parent().body
        formattedParentComment = formattedParentComment.lower()

        if any(matches in formattedParentComment for matches in triggerWords):
            print("Previous match")
            return True
        else:
            print("Checking next parent")
            return checkParentsForMatches(comment.parent())
