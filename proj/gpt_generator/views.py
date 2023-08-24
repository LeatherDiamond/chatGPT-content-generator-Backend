import os
import uuid
from base64 import b64decode

from django.conf import settings

import openai

from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import GeneratedImage, GeneratedResponse
from .serializers import GeneratedImageSerializer, GeneratedResponseSerializer


class GeneratedResponseViewSet(viewsets.ModelViewSet):
    queryset = GeneratedResponse.objects.all()
    serializer_class = GeneratedResponseSerializer

    def create(self, request, *args, **kwargs):
        user_input = request.data.get("user_input")
        num_titles = request.data.get("num_titles", 5)
        openai.api_key = os.getenv("API_KEY")

        response_messages = []

        message = f"Generate {num_titles} titles of articles for {user_input}."
        response_messages.append({"role": "user", "content": message})

        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=response_messages)
        reply1 = chat.choices[0].message.content

        response_messages.append({"role": "assistant", "content": reply1})
        response_messages.append({"role": "user", "content": f"Make agenda for every article {reply1}."})

        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=response_messages)
        reply2 = chat.choices[0].message.content

        filename = f"{uuid.uuid4()}.html"
        filepath = os.path.join(settings.STATIC_ROOT, "generated_responses", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            f.write(f"<h1>{reply2}\n</h1>\n\n\n")

        reply3 = ""

        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("-") or line[0].isdigit():
                    agenda_item = line.strip()
                    paragraph_messages = [{"role": "user", "content": f"Write a paragraph about {line}."}]
                    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=paragraph_messages)
                    reply3 = chat.choices[0].message.content

                    with open(filepath, "a") as file:
                        file.write(f"<h2>{agenda_item}</h2>\n")
                        file.write(f"<h3>{reply3}</h3>\n\n\n")

        response = GeneratedResponse(content=reply3, file_name=filename)
        response.save()

        file_absolute_path = os.path.abspath(filepath)

        return Response({"file_path": file_absolute_path}, status=status.HTTP_201_CREATED)


class GeneratedImageViewSet(viewsets.ModelViewSet):
    queryset = GeneratedImage.objects.all()
    serializer_class = GeneratedImageSerializer

    def create(self, request, *args, **kwargs):
        prompt = request.data.get("description", "")
        openai.api_key = os.getenv("API_KEY")

        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024", response_format="b64_json")
        image_data = response["data"][0]["b64_json"]

        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(settings.STATIC_ROOT, "generated_images", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as file:
            file.write(b64decode(image_data))

        image = GeneratedImage(description=prompt, image=f"generated_images/{filename}")
        image.save()

        file_absolute_path = os.path.abspath(filepath)

        return Response({"file_path": file_absolute_path}, status=status.HTTP_201_CREATED)