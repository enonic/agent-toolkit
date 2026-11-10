# Documenting library functions and types

The pattern for reference pages that document a JavaScript or TypeScript library: an Enonic XP library (`/lib/xp/...`), an npm
package such as an adapter, or any API where functions take a single object argument. Flat, linked tables; never nested tables.

## Page itinerary

Fixed top-level sections, in this order. Omit a section only when the library has nothing for it.

```text
= Library name
== Usage            (or == Install for XP libraries: how to add and import it)
== Functions        one === fnName per function
== Classes          one === ClassName per class, members as ==== memberName
== Type Definitions one === TypeName per reused type, each with an explicit anchor
== Events           only if the library emits events
== Constants        only if the library exports constants
```

Group strictly by kind. Within a function or method, use `[.lead]` labels (`Parameters`, `Returns`, `Example`) rather than
sub-headings, so the table of contents stays at the function level.

## Rules

1. **Single-object parameter.** Lead in with *"``fn()`` takes a single `params` object with these properties:"* followed by one
   flat table with the columns `Name | Type | Description`. Do not add an outer `params | object | ...` row. Do not use nested
   AsciiDoc tables (`!===`). Do not flatten sub-objects with dot notation (`schedule.value`).

2. **Required by default.** There is no "required" column. A field is required unless its description begins with
   `*Optional.*`. State conditional requirements in prose: *"\*Optional.\* ... Required when `type` is `CRON`."* Put defaults in
   the description too: *"\*Optional.\* Root path to serve from. Defaults to `+/static+`."*

3. **Inline single-use objects; break out only when reused.** A `params` or `options` shape used by one function is documented
   inline in that function. When the same shape is used by several functions, or appears in both a parameter and a return
   value, define it once under `== Type Definitions` with an explicit anchor (`[#schedule-type]`) and reference it from the
   Type column as `<<schedule-type, Schedule>>`.

4. **Return values.** The `Returns` line names the type and links to its definition:
   `*object* : (<<scheduled_job,`ScheduledJob`>>) Detail information for the job.` Do not wrap the whole line in `+...+`; that
   disables the bold type, the cross-reference and the monospace at once. Wrap only a substring that contains an underscore.

5. **Table style.** Borderless three-column tables, the same shape for parameters, return objects and type definitions:

   ```asciidoc
   [%header,cols="1%,1%,98%a"]
   [frame="none"]
   [grid="none"]
   |===
   | Name | Type | Description
   | name | string | Name of the job.
   |===
   ```

   The `a` on the third column makes it an AsciiDoc cell, so descriptions can hold inline formatting and cross-references.

6. **Examples double as sample payloads.** Keep an `Example` block per function showing a realistic call, and a `Return value`
   block where the shape is not obvious. These are what readers and LLMs copy.

7. **Version badges in cells.** A field added in a later version carries an inline badge at the start of its description:
   `image:xp-810.svg[XP 8.1.0,opts=inline] *Optional.* ...`.

## Complete example

A trimmed version of the XP scheduler library page, showing two functions and two reused types.

```asciidoc
= Scheduler library
include::../.variables.adoc[]
:toc: right
:imagesdir: ../images

Functions for creating and managing scheduled jobs.

== Install

Add the library to your `build.gradle` file:

[source,groovy]
----
dependencies {
  include xplibs.scheduler
}
----

== Functions

=== get

Returns a scheduled job with the specified name.

[.lead]
Parameters

`get()` takes a single `params` object with these properties:

[%header,cols="1%,1%,98%a"]
[frame="none"]
[grid="none"]
|===
| Name | Type | Description
| name | string | Name of the job.
|===

[.lead]
Returns

*object* : (<<scheduled_job,`ScheduledJob`>>) Detail information for the job, or null if the job could not be found.

[.lead]
Example

[source,typescript]
----
import {get as getJob} from '/lib/xp/scheduler';

const job = getJob({ name: 'myjob' });
----

=== create

Creates a scheduled job.

NOTE: This function returns immediately.

[.lead]
Parameters

`create()` takes a single `params` object with these properties:

[%header,cols="1%,1%,98%a"]
[frame="none"]
[grid="none"]
|===
| Name | Type | Description
| name | string | Unique job name.
| description | string | *Optional.* Job description.
| descriptor | string | Descriptor of the task to be scheduled.
| config | object | *Optional.* Config passed to the scheduled task.
| schedule | <<schedule-type, Schedule>> | When the task runs.
| user | string | *Optional.* Principal key of the user that submitted the task.
| enabled | boolean | Whether the job is active.
|===

[.lead]
Returns

*object* : (<<scheduled_job,`ScheduledJob`>>) Detail information for the created job.

[.lead]
Example

[source,typescript]
----
import {create} from '/lib/xp/scheduler';

const job = create({
    name: 'myjob',
    descriptor: 'appKey:task',
    enabled: true,
    schedule: {type: 'ONE_TIME', value: '2012-01-01T00:00:00.00Z'}
});
----

== Type Definitions

[[scheduled_job]]
=== ScheduledJob

[.lead]
Properties

[%header,cols="1%,1%,98%a"]
[frame="none"]
[grid="none"]
|===
| Name | Type | Description
| name | string | Job name.
| description | string | Job description.
| descriptor | string | Descriptor of the scheduled task.
| config | object | Config passed to the scheduled task.
| schedule | <<schedule-type, Schedule>> | When the task runs.
| user | string | Principal key of the user that submitted the task.
| enabled | boolean | Whether the job is active.
| lastRun | string | Time of the last job run.
|===

[#schedule-type]
=== Schedule

[.lead]
Properties

[%header,cols="1%,1%,98%a"]
[frame="none"]
[grid="none"]
|===
| Name | Type | Description
| value | string | Schedule value, in the format required by `type`.
| type | string | Schedule type: `CRON`, `ONE_TIME`, or image:xp-810.svg[XP 8.1.0,opts=inline] `FIXED_RATE`.
| timeZone | string | Time zone of the cron schedule. Required when `type` is `CRON`; not applicable to the other types.
| deleteAfterRun | boolean | image:xp-810.svg[XP 8.1.0,opts=inline] *Optional.* Whether the job deletes itself once its task has been submitted. Only applicable when `type` is `ONE_TIME`. Defaults to `false`.
|===
```

The full page is `docs/libraries/lib-scheduler.adoc` in the `enonic/doc-code` repository.

## Classes

A class is documented as `=== ClassName` under `== Classes`, with a short description, a `[.lead] Constructor` block using the
same parameter table, and each public member as `==== memberName` following the function pattern. Static members are marked
in the member's first sentence.

## Checklist for a library page

- Sections appear in the fixed order and nothing is grouped by feature instead of by kind.
- Every function has `Parameters`, `Returns` and `Example` labels, even when `Parameters` says the function takes none.
- Every table uses the borderless three-column shape.
- No `required` column; every optional field starts its description with `*Optional.*`.
- Every reused shape is defined once under `== Type Definitions` with an anchor, and every Type cell that uses it links to it.
- No nested tables and no dot-notation field names.
- Identifiers with underscores in prose or table cells are wrapped in `+...+`.
