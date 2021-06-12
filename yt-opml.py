#!/usr/bin/env python3
import argparse
import json
from xml.etree import ElementTree as et

def main():
    parser = argparse.ArgumentParser(
        description="yt-opml.py takes Google's Takeout JSON for YouTube and converts it to an OPML file. The goal is to facilitate importing the OPML file into an RSS feed reader."
    )
    parser.add_argument(
        "input",
        type=argparse.FileType("rb"),
        help="The JSON file provided by Google."
    )
    parser.add_argument(
        "output",
        type=argparse.FileType("wb"),
        help="The OPML file to be imported into an RSS feed reader."
    )
    args = parser.parse_args()
    
    # Initialize the OPML Element
    opml = et.Element("opml", version="2.0")
    head = et.SubElement(opml, "head")
    et.SubElement(head, "title").text = "YouTube Subscriptions"
    body = et.SubElement(opml, "body")

    with args.input as takeout:
        subscriptions = json.load(takeout)

        # YouTube's Takeout contains a subscriptions.json file. It's located at
        # "./Takeout/YouTube and YouTube Music/subscriptions/subscriptions.json"
        # The JSON file doesn't have a specification that I can find. It is a
        # list of subscriptions. The parts that are relevant to creating the 
        # OPML file are
        #   {
        #     "snippet": {
        #       "title",
        #       "description",
        #       "resourceId": {
        #         "channelId"
        #       }
        #     }
        #   }
        #   
        for channel in subscriptions:
            snippet = channel.get("snippet")
            resource_id = snippet.get("resourceId")
            channel_id = resource_id.get("channelId")
            
            # This command maps the elements from the JSON file to their
            # corresponding attributes in the <outline> element of an OPML file.
            et.SubElement(body, "outline",
                title=snippet.get("title"),
                text=snippet.get("title"),
                description=snippet.get("description"),
                type="rss",
                # This is the RSS feed for the channel.
                xmlUrl=f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
                # This is the channel's homepage.
                htmlUrl=f"https://www.youtube.com/channel/{channel_id}"
            )
    
    # Serialize the OPML Element to the output file
    tree = et.ElementTree(opml)
    tree.write(args.output,
        encoding="UTF-8",
        xml_declaration=True
    )

if __name__ == "__main__":
    main()
