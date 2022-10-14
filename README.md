# Bookshelf Generator

This NVIDIA Omniverse Kit Extension procedurally creates bookshelves with variable height and width and it fills the shelves with books. It is part of a series of live coding sessions that I worked on. This is a great project to study if you are interested in learning more about USD, PointInstancers and Kit Extensions. Watch the recordings of the [full Bookshelf Generator live coding series](https://www.youtube.com/playlist?list=PL3jK4xNnlCVcDS_DgtTSAljdC2KUliU1F).

![Bookshelf Generator](exts/maticodes.generator.bookshelf/data/clip.gif)

## Usage 
See the extension's README for [usage instructions](exts/maticodes.generator.bookshelf/docs/README.md).

## App Link Setup

If `app` folder link doesn't exist or broken it can be created again. For better developer experience it is recommended to create a folder link named `app` to the *Omniverse Kit* app installed from *Omniverse Launcher*. Convenience script to use is included.

Run:

```
> link_app.bat
```

If successful you should see `app` folder link in the root of this repo.

If multiple Omniverse apps is installed script will select recommended one. Or you can explicitly pass an app:

```
> link_app.bat --app create
```

You can also just pass a path to create link to:

```
> link_app.bat --path "C:/Users/bob/AppData/Local/ov/pkg/create-2021.3.4"
```

## Attribution
Icon made by [Freepik](https://www.flaticon.com/authors/freepik) from [www.flaticon.com](www.flaticon.com)

## Contributing
The source code for this repository is provided as-is and we are not accepting outside contributions.
