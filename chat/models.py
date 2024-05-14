from django.db import models
from django.utils import timezone


class Chat(models.Model):
    # Chat room model

    owner = models.OneToOneField("account.Account", on_delete=models.CASCADE, related_name="chat")
    # these are clients

    handler = models.ForeignKey("account.Account", on_delete=models.SET_NULL,
                                blank=True, null=True, related_name="clients")
    # these are the delivery people

    def __str__(self):
        return self.owner.username


class Message(models.Model):
    # a model for handling individual messages

    chat = models.ForeignKey(Chat, on_delete=models.DO_NOTHING, related_name="messages")

    sent_by = models.ForeignKey("account.Account", on_delete=models.DO_NOTHING, related_name="sent")

    sent_to = models.ForeignKey("account.Account", on_delete=models.DO_NOTHING,
                                related_name="received", null=True, blank=True)

    content = models.TextField()

    delivered = models.BooleanField(default=False)

    read = models.BooleanField(default=False)

    sent = models.DateTimeField(default=timezone.now)

    def __str__(self):
        short_content = str(self.content)
        if self.sent_to == self.chat.owner:
            chatting_with = "⇦ <" + str(self.sent_by)
        else:
            chatting_with = "⇨ <" + str(self.sent_to)
        if len(short_content) > 30:
            short_content = short_content[:30] + "..."
        return f"<{self.chat.owner}> {chatting_with}>: \"{short_content}\""

    class Meta:
        ordering = ["sent"]
