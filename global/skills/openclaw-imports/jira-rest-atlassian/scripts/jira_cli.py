#!/usr/bin/env python3
import argparse
from jira_common import JiraClient, add_env_arg, load_json_arg, print_json


def main():
    parser = argparse.ArgumentParser(description="Direct Jira REST helper")
    add_env_arg(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("myself")

    p_project = sub.add_parser("project")
    p_project.add_argument("--key", required=True)

    p_fields = sub.add_parser("fields")
    p_fields.add_argument("--query")

    p_search = sub.add_parser("search")
    p_search.add_argument("--jql", required=True)
    p_search.add_argument("--limit", type=int, default=50)
    p_search.add_argument("--fields")

    p_issue_get = sub.add_parser("issue-get")
    p_issue_get.add_argument("key")
    p_issue_get.add_argument("--expand")

    p_issue_update = sub.add_parser("issue-update")
    p_issue_update.add_argument("key")
    p_issue_update.add_argument("--fields", required=True, help="JSON string or @file.json")

    p_issue_comment = sub.add_parser("issue-comment")
    p_issue_comment.add_argument("key")
    p_issue_comment.add_argument("--body", required=True)

    p_transitions = sub.add_parser("transitions")
    p_transitions.add_argument("key")

    p_transition = sub.add_parser("transition")
    p_transition.add_argument("key")
    group = p_transition.add_mutually_exclusive_group(required=True)
    group.add_argument("--id")
    group.add_argument("--name")

    p_create = sub.add_parser("issue-create")
    p_create.add_argument("--payload", required=True, help="JSON string or @file.json")

    args = parser.parse_args()
    client = JiraClient(args.env_file)

    if args.command == "myself":
        print_json(client.myself())
        return

    if args.command == "project":
        print_json(client.project(args.key))
        return

    if args.command == "fields":
        fields = client.fields()
        if args.query:
            query = args.query.lower()
            fields = [f for f in fields if query in (f.get("name", "") + " " + f.get("id", "")).lower()]
        print_json(fields)
        return

    if args.command == "search":
        print_json(client.search(args.jql, limit=args.limit, fields=args.fields))
        return

    if args.command == "issue-get":
        print_json(client.issue_get(args.key, expand=args.expand))
        return

    if args.command == "issue-update":
        print_json(client.issue_update(args.key, load_json_arg(args.fields)))
        return

    if args.command == "issue-comment":
        print_json(client.issue_comment(args.key, args.body))
        return

    if args.command == "transitions":
        print_json(client.transitions(args.key))
        return

    if args.command == "transition":
        if args.id:
            transition_id = args.id
        else:
            transitions = client.transitions(args.key).get("transitions", [])
            wanted = args.name.strip().lower()
            matched = next((t for t in transitions if t.get("name", "").strip().lower() == wanted), None)
            if not matched:
                raise SystemExit(f"No transition named '{args.name}' for {args.key}")
            transition_id = matched["id"]
        print_json(client.transition(args.key, transition_id))
        return

    if args.command == "issue-create":
        print_json(client.issue_create(load_json_arg(args.payload)))
        return


if __name__ == "__main__":
    main()
