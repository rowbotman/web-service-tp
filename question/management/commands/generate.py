import os
import random
import faker

from django.core.files import File
from django.core.management import BaseCommand, CommandError

from question.models import User, Post as Question, Answer, Tag, QuestionVote, \
    AnswerVote


def generate_users(n_users, img_dir, _password='12345'):
    fake_generator = faker.Faker()
    imgs = [os.path.join(img_dir, x) for x in os.listdir(img_dir)]
    for i in range(n_users):
        while True:
            name = fake_generator.name()
            if User.objects.filter(
                    username=name.replace(' ', '')).first() is None:
                break
        email = fake_generator.email()
        password = _password() if callable(_password) else _password
        upload_name = random.choice(imgs)
        upload_file = open(upload_name, 'rb')
        upload_name = os.path.split(upload_name)[-1]
        u = User.objects.create_user(
            name.replace(' ', ''), email, password,
            first_name=name.split()[0],
            last_name=name.split()[1]
        )
        u.upload.save(upload_name, File(upload_file))
        u.save()
        print(f"[{i+1}/{n_users}] Saved user {u} (avatar at {u.upload.url})")


def generate_tags(n_tags):
    fake_generator = faker.Faker()
    for i in range(n_tags):
        while True:
            n_words = random.randint(1, 4)
            tag_name = ' '.join(fake_generator.word() for _ in range(n_words))
            if Tag.objects.filter(title=tag_name).first() is None:
                break
        tag = Tag(title=tag_name)
        tag.save()
        print(f"[{i+1}/{n_tags}] Saved tag {tag}")


def generate_posts(n_posts, text_length_limits=(4, 15), n_tags_limits=(1, 7),
                   tags=None, users=None):
    fake_generator = faker.Faker()
    if tags is None:
        tags = list(Tag.objects.all()[:])
    assert len(tags) >= n_tags_limits[1], \
        f"Not enough tags ({len(tags)}, should be at least" \
        f" {n_tags_limits[1]}) (set in parameters)"

    if users is None:
        users = list(User.objects.all()[:])
    assert len(users) > 0, "Need at least one author to create posts"

    for i in range(n_posts):
        text_length = random.randint(*text_length_limits)
        text = ' '.join(
            fake_generator.text() for _ in range(text_length))
        n_tags = random.randint(*n_tags_limits)
        post_tags = random.sample(tags, n_tags)
        post_author = random.choice(users)
        title = fake_generator.sentence()
        q = Question(text=text, title=title, author=post_author)
        q.save()
        q.add_tags(post_tags)
        print(f"[{i+1}/{n_posts}] Saved {q} by {post_author}"
              f" with {n_tags} tags and {text_length} texts concatenated")


def generate_answers(posts=None, text_length_limits=(1, 5),
                     answer_per_question_limits=(0, 12), users=None):
    fake_generator = faker.Faker()
    if posts is None:
        posts = list(Question.objects.all()[:])

    if users is None:
        users = list(User.objects.all()[:])
    assert len(users) > 0, "Need at least one author to create answers"

    for i, question in enumerate(posts):
        n_answers = random.randint(*answer_per_question_limits)
        for j in range(n_answers):
            text_length = random.randint(*text_length_limits)
            text = ' '.join(
                fake_generator.text() for _ in range(text_length))
            post_author = random.choice(users)
            a = Answer(text=text, question=question, author=post_author)
            a.save()
            print(
                f"[{i+1}/{len(posts)}; {j+1}/{n_answers}] Saved {a} by "
                f"{post_author} to  question #{question.pk}({text_length} "
                "texts concatenated)")


def generate_post_votes(posts=None, rating_limits=(-15, 100), users=None):
    if posts is None:
        posts = list(Question.objects.all()[:])
    assert len(posts) > 0, "Nothing to vote for"

    if users is None:
        users = list(User.objects.all()[:])
    assert len(users) > 1.5 * max(abs(rating_limits[0]), abs(rating_limits[1])), \
        "Need at least one author to create answers"

    for i, post in enumerate(posts):
        final_rating = random.randint(*rating_limits)
        if final_rating > 0:
            n_downvotes = final_rating // 4
            n_upvotes = final_rating + n_downvotes
        else:
            n_upvotes = abs(final_rating) // 4
            n_downvotes = abs(final_rating + n_upvotes)
        total_votes = n_downvotes + n_upvotes
        authors = random.sample(users, total_votes)
        print(f"[{i+1}/{len(posts)}] Bringing #{post.pk} to {final_rating} "
              f"({n_upvotes} up and {n_downvotes} down)")
        for j in range(n_downvotes):
            QuestionVote(author=authors[j], question=post, value=-1).save()
            print(
                f"[{i+1}/{len(posts)}; {j+1}/{total_votes}] Voted"
                f" down for #{post.pk})")

        for j in range(n_upvotes):
            try:
                QuestionVote(author=authors[j + n_downvotes], question=post,
                             value=1).save()
            except:
                pass
            print(
                f"[{i+1}/{len(posts)}; {j+1 + n_downvotes}/{total_votes}] Voted"
                f" up for #{post.pk})")


def generate_answer_votes(posts=None, rating_limits=(-4, 12), users=None):
    if posts is None:
        posts = list(Question.objects.all()[:])
    assert len(posts) > 0, "Nothing to vote for"

    if users is None:
        users = list(User.objects.all()[:])
    assert len(users) > 1.5 * max(abs(rating_limits[0]), abs(rating_limits[1])), \
        "Need at least one author to create answers"

    for i, post in enumerate(posts):
        answers = list(post.answer_set.all())
        for a, answer in enumerate(answers):
            final_rating = random.randint(*rating_limits)
            if final_rating > 0:
                n_downvotes = final_rating // 4
                n_upvotes = final_rating + n_downvotes
            else:
                n_upvotes = abs(final_rating) // 4
                n_downvotes = abs(final_rating + n_upvotes)
            total_votes = n_downvotes + n_upvotes
            authors = random.sample(users, total_votes)
            print(f"[{i+1}/{len(posts)}; {a+1}/{len(answers)}]"
                  f" Bringing A#{answer.pk} to Q#{post.pk}"
                  f" to {final_rating} ({n_upvotes} up and {n_downvotes} down)")
            for j in range(n_downvotes):
                AnswerVote(author=authors[j], answer=answer, value=-1).save()
                print(
                    f"[{i+1}/{len(posts)}; {a+1}/{len(answers)}"
                    f"; {j+1}/{total_votes}] Voted down for #{post.pk})")

            for j in range(n_upvotes):
                AnswerVote(author=authors[j + n_downvotes], answer=answer,
                           value=1).save()
                print(
                    f"[{i+1}/{len(posts)}; {a+1}/{len(answers)}; "
                    f"{j+1 + n_downvotes}/{total_votes}] Voted up for #{post.pk})")


class Command(BaseCommand):
    help = 'You moron'

    def handle(self, *args, **options):
        n_users = 0
        img_dir = '/home/astronaut/gitLab/web-service-hw/media/'
        n_posts = 0
        n_answers = 100
        n_tags = 0
        gen_question_votes = False
        gen_answer_votes = False

        if n_users:
            if not img_dir: raise CommandError
            generate_users(n_users, img_dir)

        if n_tags:
            generate_tags(n_tags)

        if n_posts:
            generate_posts(n_posts)

        if n_answers:
            generate_answers(n_answers)

        if gen_question_votes:
            generate_post_votes()

        if gen_answer_votes:
            generate_answer_votes()
