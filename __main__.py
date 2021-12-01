"""
    :author: pbouillon  [https:/pbouillon.github.io/]
    :license: Unlicense [See LICENSE.txt]
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import choice, shuffle
from typing import List, Dict

from student import Student
from utils import Mail

BASE_DATA_FILE = './data/students.txt'
MAIL_DOMAIN = '@telecomnancy.net'


def fetch_participants(data_file: str = BASE_DATA_FILE) -> List[Student]:
    """Create the list of all participant from a source file

    :param data_file: Source file (one name per line)
    :return: The list of participants as a list of `Student`
    """
    participants: List[Student] = []

    with open(data_file, 'r') as name_file:
        for name in name_file:
            name = name.strip()
            mail_addr = name.replace(' ', '.') + MAIL_DOMAIN
            participants.append(Student(name, mail_addr))

    return participants


def generate_combinations(subjects: List[Student]) -> List[List[Student]]:
    """Generate the pairs of [secret santas -> good kiddo]

    :param subjects: Students from whom the pairs should be generated
    :return: A list of all pairs
    """
    # Create the initial graph as: a student can be matched with any other excepted himself
    graph: Dict[Student, List[Student]] = {
        target: [student for student in subjects if subjects != student]
        for target in subjects
    }

    # Shuffle affectations to add randomness
    for _, connections in graph.items():
        shuffle(connections)

    # Randomly pick the source node
    source_node: Student = choice(subjects)

    # Generate the chains of affectation
    to_be_affected = subjects[:]

    # Initialize the sequence
    affectations = [source_node]
    to_be_affected.remove(source_node)

    # Iterate over the students
    potential = None
    while len(to_be_affected) != 0:
        # Pick the next student not already affected
        for potential in graph[affectations[-1]]:
            if potential in affectations:
                continue
            # Exit the loop when found
            break

        affectations.append(potential)
        to_be_affected.remove(potential)

    # Assert that all subjects are affected
    assert len(affectations) == len(subjects)

    # Generate pairs from the found affectations
    return [
        [affectations[i], affectations[(i + 1) % len(affectations)]]
        for i in range(len(affectations))]


def generate_mail_content(receiver: Student, assigned: Student) -> bytes:
    """Generate the appropriate mail for the receiver

    :param receiver: Receiver of the mail
    :param assigned: Student assigned to the receiver
    :return: The encoded message to send to the receiver
    """
    return '\n'.join((
        f'Ho ho ho {receiver.first_name()} ! 🎅',
        '',
        'Prêt pour le retour des Pères (et Mères) Noël secret.e.s ? 🤶',
        '',
        'Avant tout, petit rappel des règles (on fait monter le suspens):',
        '\t- Pour les cadeaux, l\'idéal est de ne pas dépasser une dizaine d\'euros (même si bon, on est apprentis)',
        '\t- Évidemment, et même si c\'est super tentant: ne dis pas qui tu as ! Ça gâcherait vraiment le coté',
        '\t  fun du jeu si tout le monde sait à l\'avance (surtout la personne concernée !)',
        '\t- Enfin, si jamais il y a le moindre soucis, n\'hésite pas à venir m\'en parler 🚑',
        '',
        f'Sans plus de suspens, tu seras le Père Noël secret de ... {assigned.fullname.upper()} !',
        'Cette année le jour du déballage sera le 13 décembre.',
        '',
        'Bon courage pour trouver un joli cadeau, et joyeux Noël en avance !',
        '',
        '⛄ 🎄🦌 ⛄'))\
        .encode('utf-8')


def notify_selected_users(pairs: List[List[Student]]) -> None:
    """Send a mail to each secret santa with the name of person to surprise

    :param pairs: Pairs of students as [santa, to_suprise]
    :return: None
    """
    # Establish connection with the SMTP server
    server = smtplib.SMTP(Mail.SERVER_ADDR, Mail.SERVER_PORT)
    server.ehlo()
    server.starttls()
    server.login(Mail.Credentials.LOGIN, Mail.Credentials.PASSWORD)

    total_sent = 0

    print('[BEGIN]')

    # Send all mails
    for santa, kiddo in pairs:
        total_sent += 1

        # Mail creation
        mail = MIMEMultipart('alternative')

        mail['From'] = Mail.SENDER
        mail['To'] = Mail.RECIPIENT

        mail['Subject'] = Mail.SUBJECT

        mail.attach(
            MIMEText(
                generate_mail_content(santa, kiddo),
                _charset='utf-8'))

        # Mail sending
        server.sendmail(
            Mail.SENDER,
            santa.mail,
            mail.as_string())

        print(f'[SEND] {santa.fullname}')

    print(f'[DONE] Sent: {total_sent}')

    # End connection
    server.close()


def main() -> None:
    """Program entry point
    """
    participants = fetch_participants()

    assignations = generate_combinations(participants)

    notify_selected_users(assignations)


if __name__ == '__main__':
    main()
