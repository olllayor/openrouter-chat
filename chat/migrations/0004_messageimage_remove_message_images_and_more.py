# Generated by Django 5.1.5 on 2025-02-06 17:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0003_message_images"),
    ]

    operations = [
        migrations.CreateModel(
            name="MessageImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="aichat_images/")),
            ],
        ),
        migrations.RemoveField(
            model_name="message",
            name="images",
        ),
        migrations.AddField(
            model_name="message",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(
                fields=["created_at"], name="chat_messag_created_b6b51c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["sender"], name="chat_messag_sender_666dde_idx"),
        ),
        migrations.AddField(
            model_name="messageimage",
            name="message",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="chat.message",
            ),
        ),
    ]
