from django.shortcuts import render, redirect
from django import forms
import random
from . import util



# Forms
class search(forms.Form):
    search = forms.CharField(label="Search wiki",
        widget=forms.TextInput(attrs={"placeholder": "Type entry here"}))

class NewPageForm(forms.Form):
    title = forms.CharField(label="Page Title",
        widget=forms.TextInput(attrs={"placeholder": "Enter Title"}))
    
    content = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Enter Content"}))

class EditForm(forms.Form):
    new_content = forms.CharField( label="Content",
        widget=forms.Textarea(attrs={"placeholder": "Enter Content"}),
    )




# Entries and main pages
def index(request):
    if request.method == 'POST':
        form = search(request.POST)
        if form.is_valid():
            query = form.cleaned_data["search"]
        else:
            return render(request, "encyclopedia/index.html", {
                "form": form,
                "POST": "Search"
            })
        
        results = []
        no_results = ""
        for entry in util.list_entries():
            if query.lower() == entry.lower():
                return render(request, f"encyclopedia/{entry}.html", {
                    "Content": util.get_entry(f"{entry}"),
                    "form": search(),
                    "POST": "Search"
                })
            elif query.lower() in entry.lower():
                results.append(entry)
        if results == []:
            no_results = "Sorry, No results were found :("
        return render(request, "encyclopedia/search_results.html", {
            "Results": results,
            "apology":no_results,
            "length": len(results),
            "form": search(),
            "POST": "Search"
            })
            
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": search(),
        "POST": "Search"
    })

def entry(request, entry):
    if request.method == 'POST':
        form = search(request.POST)
        if form.is_valid():
            query = form.cleaned_data["search"]
        else:
            return redirect("/")
        
        results = []
        no_results = ""
        for e in util.list_entries():
            if query.lower() == e.lower():
                return render(request, f"encyclopedia/{e}.html", {
                    "Content": util.get_entry(f"{e}"),
                    "form": search(),
                    "POST": "Search"
                })
            elif query.lower() in e.lower():
                results.append(e)
        if results == []:
            no_results = "Sorry, No results were found :("
        return render(request, "encyclopedia/search_results.html", {
            "Results": results,
            "apology":no_results,
            "length": len(results),
            "form": search(),
            "POST": "Search"
            })    
    for e in util.list_entries():    
        if e.lower() == entry.lower():
            return render(request, f"encyclopedia/{entry}.html", {
                "form": search()
            })
    
    return render(request, "encyclopedia/not_found.html", {
        "apology": "Page not found :(",
        "form": search(),
        "POST": "Search"
        })

def RandomPage(request):
    if request.method == 'POST':
        form = search(request.POST)
        if form.is_valid():
            query = form.cleaned_data["search"]
        else:
            return render(request, "encyclopedia/index.html", {
                "form": form,
                "POST": "Search"
            })
        
        results = []
        no_results = ""
        for entry in util.list_entries():
            if query.lower() == entry.lower():
                return render(request, f"encyclopedia/{entry}.html", {
                    "Content": util.get_entry(f"{entry}"),
                    "form": search(),
                    "POST": "Search"
                })
            elif query.lower() in entry.lower():
                results.append(entry)
        if results == []:
            no_results = "Sorry, No results were found :("
        return render(request, "encyclopedia/search_results.html", {
            "Results": results,
            "apology":no_results,
            "length": len(results),
            "form": search(),
            "POST": "Search"
            })
    page = random.choice(util.list_entries())
    return render(request, f"encyclopedia/{page}.html", {
        "Content": util.get_entry(f"{page}"),
        "form": search(),
        "POST": "Search"
    })


def edit(request, entry):
    
    old_content = util.get_entry(entry)
    form = EditForm(initial={"new_content" : f"{old_content}"})



    if request.method == "POST":
        edited = EditForm(request.POST)
        if edited.is_valid():
            new_content = edited.cleaned_data["new_content"]
        else:
            return redirect("/")


        util.save_entry(entry, new_content)
        f = open(f"encyclopedia/templates/encyclopedia/{entry}.html", "r+")
        f.write(template(entry, new_content))
        f.close()

        return render(request, "encyclopedia/edited.html", {
            "title": entry
        })
        


    return render(request, f"edit/{entry}.html", {
        "EditForm": form
    })


def NewPage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
        else:
            return redirect("/")
        
        for entry in util.list_entries():
            if title.lower() == entry.lower():
                return render(request, "encyclopedia/apology.html" , {
                    "title": entry
                })
            
        util.save_entry(title, content)
        f = open(f"encyclopedia/templates/encyclopedia/{title}.html", "x")
        f.write(template(title, content))
        f.close()

        f = open(f"encyclopedia/templates/edit/{title}.html", "x")
        f.write(edit_template(title))
        
        return render(request, "encyclopedia/created.html", {
            "title": title
        })
        
        
    return render(request, "encyclopedia/NewPage.html", {
        "NewPageForm": NewPageForm(),
        "POST": "Save Page"
    })




























def template(title, content):
    html = f'''
                        {{% extends "encyclopedia/layout.html" %}}

                        {{% block title %}}
                            {title}
                        {{% endblock %}}

                        {{% block body %}}
                        <h1>{title}</h1>    
                            {content}
                        {{% endblock %}}

                        {{% block nav %}}
                            <a href="/edit/{title}">Edit Page</a>
                        {{% endblock %}}

                        {{% block post %}}
                            <button type="submit" class="btn btn-primary">Search</button>
                        {{% endblock %}}

                '''
    return html



def edit_template(title):
    html = f''' 
        
        {{% load static %}}

                        <!DOCTYPE html>

                        <html lang="en">
                            <head>
                                <title>Create New Page</title>
                                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
                                <link href="{{% static 'encyclopedia/styles.css' %}}" rel="stylesheet">
                            </head>
                            <body>
                                <div class="row">
                                    <div class="sidebar col-lg-2 col-md-3">
                                        <h2>Wiki</h2>
                                        <br>
                                        <div>
                                            <a href="{{% url 'index' %}}">Home</a>
                                        </div>
                                        <div>
                                            <a href="{{% url 'NewPage' %}}">Create New Page</a>
                                        </div>
                                        <div>
                                            <a href="{{% url 'RandomPage' %}}">Random Page</a>
                                        </div>
                                    </div>
                                    <div class="main col-lg-10 col-md-9">
                                        <form method="post" action="/edit/{title}" >
                                            {{% csrf_token %}}
                                            <div class="form-group">
                                                {{{{ EditForm }}}}
                                            </div>
                                            <button type="submit" class="btn btn-primary">Finish Edit</button>
                                        </form>
                                    </div>
                                </div>

                            </body>
                        </html>
        
        '''
    return html