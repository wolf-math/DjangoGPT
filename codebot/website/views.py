from django.contrib import messages
from django.shortcuts import render, redirect
from openai import OpenAI
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from .models import Code
import os

OPENAI = os.environ.get("OPENAI")

# from asyncCall import asyncCall
lang_list = [
    "bash",
    "c",
    "clike",
    "css",
    "django",
    "docker",
    "firestore-security-rules",
    "git",
    "javascript",
    "jsx",
    "latex",
    "markup",
    "markup-templating",
    "nix",
    "php",
    "python",
    "regex",
    "ruby",
    "sql",
    "tsx",
    "typescript",
]


def forgot(request, code, lang, page):
    if lang not in lang_list:
        messages.success(request, "You forgot a programming language!")
        return render(
            request,
            f"{page}.html",
            {"lang_list": lang_list, "code": code, "lang": lang},
        )


def home(request):
    if request.method == "POST":
        code = request.POST["code"]
        lang = request.POST["lang"]

        forgot(request, code, lang, 'home')

        # OPENAI
        client = OpenAI(
                api_key=OPENAI
            )

        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f'''Respond only with code.
                        Fix this {lang} code: {code}.
                        Do not add an explanation
                        ''',
                    }
                ],
                model="gpt-3.5-turbo",
            )

            if response.choices:
                message_content = response.choices[0].message.content
            else:
                message_content = "No response received."

            record = Code(
                question=code,
                code_answer=message_content,
                language=lang,
                user=request.user
                )
            record.save()

            return render(
                request,
                "home.html",
                {
                    "lang_list": lang_list,
                    "response": message_content,
                    "code": code,
                    "lang": lang,
                },
            )

        except Exception as e:
            return render(
                request,
                "home.html",
                {
                    "lang_list": lang_list,
                    "response": e,
                    "code": code,
                    "lang": lang},
            )

    return render(request, "home.html", {"lang_list": lang_list})


def suggest(request):

    if request.method == "POST":
        code = request.POST["code"]
        lang = request.POST["lang"]

        forgot(request, code, lang, 'suggest')

        # OPENAI
        client = OpenAI(
                api_key="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"
            )
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Respond only with code. {code}.",
                    }
                ],
                model="gpt-3.5-turbo",
            )

            if response.choices:
                message_content = response.choices[0].message.content
            else:
                message_content = "No response received."

            record = Code(
                question=code,
                code_answer=message_content,
                language=lang,
                user=request.user
                )
            record.save()

            return render(
                request,
                "suggest.html",
                {
                    "lang_list": lang_list,
                    # Passing the extracted message content
                    "response": message_content,
                    "code": code,
                    "lang": lang,
                },
            )

        except Exception as e:
            return render(
                request,
                "suggest.html",
                {"lang_list": lang_list,
                    "response": e,
                    "code": code,
                    "lang": lang},
            )

    return render(request, "suggest.html", {"lang_list": lang_list})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You're Logged In!!!")
            return redirect('home')
        else:
            messages.success(request, "You couldn't log in :(")
            return redirect('home')
    else:
        return render(request, 'home.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "You logged out")
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have registerred")
            return redirect('home')
    else:
        form = SignUpForm

    return render(request, 'register.html', {"form": form})


def history(request):
    if request.user.is_authenticated:
        codes = Code.objects.filter(user_id=request.user.id)
        return render(request, 'history.html', {"codes": codes})
    else:
        messages.success(request, "You're not logged in")
        return redirect('home')


def delete_history(request, History_id):
    history = Code.objects.get(pk=History_id)
    history.delete()
    messages.success(request, "succesfully deleted")
    return redirect('history')