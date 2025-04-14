<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Supadata YouTube API Endpoints Documentation

The Supadata API offers a powerful suite of endpoints specifically designed for extracting and processing content from YouTube videos. This comprehensive documentation details each YouTube-related endpoint, their parameters, response formats, and implementation examples to facilitate seamless integration with applications requiring YouTube data extraction capabilities.

## Authentication and General Information

All API requests to Supadata require authentication using an API key. To make any request to the endpoints documented below, you must include your API key in the request headers[^1][^2].

### API Key Setup

```
curl -H "x-api-key: YOUR_API_KEY" https://api.supadata.ai/v1/...
```

To obtain an API key:

1. Sign up for an account at dash.supadata.ai
2. Choose a subscription plan
3. Your API key will be generated automatically[^1][^2]

### Base URL

All API endpoints use the following base URL:

```
https://api.supadata.ai/v1
```


### Rate Limits

API requests are rate-limited based on your subscription plan. Current limits are shown in the pricing page, and it is possible to increase rate limits upon request[^1][^2].

### Response Format

All API responses are returned in JSON format[^1][^2].

## Transcript Endpoints

### Get Transcript

This endpoint fetches transcript/subtitles from YouTube videos in various formats and languages[^5].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/transcript
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| url | string | Yes* | YouTube video URL |
| videoId | string | Yes* | YouTube video ID (alternative to URL) |
| lang | string | No | Preferred language code (ISO 639-1) |
| text | boolean | No | When true, returns plain text transcript (Default: false) |
| chunkSize | number | No | Maximum characters per transcript chunk (only when text=false) |

*Either `url` or `videoId` must be provided[^5].

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&amp;text=true' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

When text=true:

```json
{
  "content": "Never gonna give you up, never gonna let you down...",
  "lang": "en",
  "availableLangs": ["en", "es", "zh-TW"]
}
```

When text=false:

```json
{
  "content": [
    {
      "text": "[Music]",
      "offset": 0,
      "duration": 14650,
      "lang": "en"
    },
    {
      "text": "We're no strangers to",
      "offset": 18800,
      "duration": 1000,
      "lang": "en"
    }
    // Additional transcript segments...
  ],
  "lang": "en",
  "availableLangs": ["en", "es", "zh-TW"]
}
```


### Get Transcript Translation

This endpoint fetches transcript/subtitles from a YouTube video and translates it to the specified language[^10].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/transcript/translation
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| url | string | Yes* | YouTube video URL |
| videoId | string | Yes* | YouTube video ID (alternative to URL) |
| lang | string | Yes | ISO 639-1 language code of the translation |
| text | boolean | No | When true, returns plain text transcript (Default: false) |
| chunkSize | number | No | Maximum characters per transcript chunk (only when text=false) |

*Either `url` or `videoId` must be provided[^10].

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/transcript/translation?videoId=dQw4w9WgXcQ&amp;lang=es&amp;text=true' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

When text=true:

```json
{
  "content": "Nunca voy a abandonarte, nunca voy a decepcionarte…",
  "lang": "es"
}
```

When text=false:

```json
{
  "content": [
    {
      "text": "[Música]",
      "offset": 0,
      "duration": 14650,
      "lang": "es"
    }
    // Additional translated segments...
  ],
  "lang": "es"
}
```


#### Latency Considerations

Due to the duration of transcript translation tasks, this endpoint may take 20 or more seconds to complete. Be sure to increase request timeout settings in your application accordingly[^10].

## Batch Operations

The batch endpoints allow processing multiple YouTube videos in a single request. This is particularly useful for analyzing entire playlists or channels. Batch operations are asynchronous and return a job ID for checking results[^4].

### Transcript Batch

#### Endpoint Specification

```
POST /v1/youtube/transcript/batch
```


#### Request Body

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| videoIds | array | One of these is required | Array of YouTube video IDs or URLs |
| playlistId | string | One of these is required | YouTube playlist URL or ID |
| channelId | string | One of these is required | YouTube channel URL, handle or ID |
| limit | number | No | Maximum number of videos to process (Default: 10, Max: 5000) |
| lang | string | No | Preferred language code for transcripts (ISO 639-1) |
| text | boolean | No | When true, returns plain text transcript (Default: false) |

#### Example Request

```
curl -X POST 'https://api.supadata.ai/v1/youtube/transcript/batch' \
-H 'x-api-key: YOUR_API_KEY' \
-H 'Content-Type: application/json' \
-d '{
  "videoIds": [
    "dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=xvFZjo5PgG0"
  ],
  "lang": "en",
  "text": true
}'
```


#### Response

```json
{
  "jobId": "123e4567-e89b-12d3-a456-426614174000"
}
```


### Video Metadata Batch

Supadata also provides a batch endpoint for retrieving metadata from multiple YouTube videos[^4].

#### Endpoint Specification

```
POST /v1/youtube/video/batch
```

The request body parameters are similar to the transcript batch endpoint, allowing for processing videos from multiple sources (individual videos, playlists, or channels)[^4].

## Channel Operations

### Get Channel Videos

This endpoint returns a list of video IDs from a YouTube channel[^6].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/channel/videos
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| id | string | Yes | YouTube channel URL, handle or ID |
| limit | number | No | Maximum number of video IDs (Default: 30, Max: 5000) |
| type | enum | No | `all`, `video`, `short` (Default: `all`) |

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/channel/videos?id=RickAstleyVEVO&amp;limit=50' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

```json
{
  "videoIds": ["dQw4w9WgXcQ", "xvFZjo5PgG0"],
  "shortIds": ["xvFZjo5PgG0", "dQw4w9WgXcQ"]
}
```

When fetching `type: all`, the limit parameter applies to vertical videos first. For example, if the channel has 100 vertical videos and 100 Shorts, and `limit` is 150, then 100 vertical videos and 50 Shorts will be returned[^6].

### Get Channel Metadata

This endpoint returns metadata from YouTube channels including name, description, subscriber count, video count, and more[^13].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/channel
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| id | string | Yes | YouTube channel URL, handle or ID |

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/channel?id=RickAstleyVEVO' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

```json
{
  "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "name": "Rick Astley",
  "description": "The official Rick Astley YouTube channel",
  "subscriberCount": 2000000,
  "videoCount": 100,
  "thumbnail": "https://yt3.ggpht.com/...",
  "banner": "https://yt3.ggpht.com/..."
}
```


## Playlist Operations

### Get Playlist Videos

This endpoint returns a list of video IDs from a YouTube playlist[^8].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/playlist/videos
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| id | string | Yes | YouTube playlist URL or ID |
| limit | number | No | Maximum number of video IDs (Default: 100, Max: 5000) |

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/playlist/videos?id=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc&amp;limit=20' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

```json
{
  "videoIds": ["dQw4w9WgXcQ", "xvFZjo5PgG0"],
  "shortIds": ["xvFZjo5PgG0", "dQw4w9WgXcQ"]
}
```


### Get Playlist Metadata

This endpoint returns metadata from YouTube playlists including title, description, video count, view count, and more[^14].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/playlist
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| id | string | Yes | YouTube playlist URL or ID |

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/playlist?id=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

```json
{
  "id": "PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc",
  "title": "My Favorite Videos",
  "description": "A collection of my favorite videos",
  "videoCount": 25,
  "viewCount": 1000000,
  "lastUpdated": "2023-01-01T00:00:00.000Z",
  "channel": {
    "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "name": "Rick Astley"
  }
}
```


## Video Operations

### Get Video Metadata

This endpoint returns metadata from YouTube videos including title, description, channel information, view counts, and more[^12].

#### Endpoint Specification

```
GET https://api.supadata.ai/v1/youtube/video
```


#### Query Parameters

| Parameter | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| id | string | Yes | YouTube video URL or ID |

#### Example Request

```
curl -X GET 'https://api.supadata.ai/v1/youtube/video?id=dQw4w9WgXcQ' \
-H 'x-api-key: YOUR_API_KEY'
```


#### Response Format

```json
{
  "id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "description": "The official music video for \"Never Gonna Give You Up\"...",
  "duration": 213,
  "channel": {
    "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "name": "Rick Astley"
  },
  "tags": ["Rick Astley", "Official Video", "Music"],
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
  "uploadDate": "2009-10-25T00:00:00.000Z",
  "viewCount": 1234567890,
  "likeCount": 12345678,
  "transcriptLanguages": ["en", "es", "fr"]
}
```


## Supported URL Formats

The Supadata API supports various input formats for referencing videos, playlists, and channels[^15]:

### Videos

- YouTube video URL: `https://youtube.com/watch?v=dQw4w9WgXcQ`
- Short URL: `http://youtu.be/dQw4w9WgXcQ`
- Shorts URL: `https://youtube.com/shorts/dQw4w9WgXcQ`
- Embed URL: `http://www.youtube.com/embed/dQw4w9WgXcQ`
- Video ID: `dQw4w9WgXcQ`


### Playlists

- Playlist URL: `https://youtube.com/playlist?list=PL9tY0BWXOZFuFEG_GtOBZ8-8wbkH-NVAr`
- Playlist ID: `PL9tY0BWXOZFuFEG_GtOBZ8-8wbkH-NVAr`


### Channels

- Channel URL: `https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw`
- Custom URL: `https://youtube.com/c/RickAstley`
- Handle URL: `https://youtube.com/@RickAstley`
- Channel ID: `UCuAXFkgsw1L7xaCfnd5JJOw`


### Unsupported Content Types

- Live videos
- Private videos
- User profile links[^15]


## Alternative Python SDK

For Python developers, a Python SDK called `youtube-transcript-api` is available with similar functionality[^9]. It offers methods to:

- Fetch transcripts: `YouTubeTranscriptApi().fetch(video_id)`
- List available transcripts: `YouTubeTranscriptApi().list(video_id)`
- Find transcripts in specific languages: `transcript_list.find_transcript(['de', 'en'])`
- Translate transcripts: `transcript.translate('de')`


## Pricing Information

Supadata operates on a credit-based pricing model where each API request consumes a specific number of credits:

- 1 video metadata request = 1 credit[^12]
- 1 channel metadata request = 1 credit[^13]
- 1 playlist metadata request = 1 credit[^14]
- 1 channel videos request = 1 credit[^6]
- 1 playlist videos request = 1 credit[^8]


## Conclusion

The Supadata YouTube API provides a comprehensive set of endpoints for extracting and processing YouTube content. From fetching video transcripts and translations to retrieving channel and playlist metadata, the API offers a robust solution for applications requiring YouTube data. With support for batch operations and various URL formats, developers can efficiently integrate YouTube content into their applications with minimal effort.

When implementing these endpoints, remember to properly authenticate all requests with your API key, respect rate limits based on your subscription plan, and consider the specific requirements of your application to determine which endpoints and parameters best suit your needs.

<div>⁂</div>

[^1]: https://supadata.ai/documentation/getting-started

[^2]: https://supadata.ai/documentation/getting-started

[^3]: https://supadata.ai/youtube-transcript-api

[^4]: https://supadata.ai/documentation/youtube/batch

[^5]: https://supadata.ai/documentation/youtube/get-transcript

[^6]: https://supadata.ai/documentation/youtube/channel-videos

[^7]: https://devhunt.org/tool/youtube-transcript-api

[^8]: https://supadata.ai/documentation/youtube/playlist-videos

[^9]: https://pypi.org/project/youtube-transcript-api/

[^10]: https://supadata.ai/documentation/youtube/get-transcript-translation

[^11]: https://apify.com/karamelo/youtube-transcripts/api

[^12]: https://supadata.ai/documentation/youtube/video

[^13]: https://supadata.ai/documentation/youtube/channel

[^14]: https://supadata.ai/documentation/youtube/playlist

[^15]: https://supadata.ai/documentation/youtube/supported-url-formats

[^16]: https://rapidapi.com/8v2FWW4H6AmKw89/api/youtube-transcripts

[^17]: https://community.n8n.io/t/youtube-transcript-text/92463

[^18]: https://www.reddit.com/r/SideProject/comments/1ecg9f0/ive_created_a_free_tool_for_extracting_youtube/

[^19]: https://rapidapi.com/8v2FWW4H6AmKw89/api/ai-content-scraper

[^20]: https://developers.google.com/youtube/v3/docs

[^21]: https://supadata.ai/documentation/youtube/supported-language-codes

