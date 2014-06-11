
require "logstash/filters/base"
require "logstash/namespace"

# This filter is a mildly hackish workaround for wrongly character encoded event data
# and the issues it causes in the logstash pipeline. (See: LOGSTASH-1443,LOGSTASH-1308
# LOGSTASH-1353, etc)
#
# Simply list the event fields that are causing you problems, along with a tag to
# attach for offending events, like so:
#
#    force_encoding {
#        fields => ["path","qstring","message","referrer"]
#        tag => "_argh_wtf-8_encoding!"
#    }
#
# Any wrongly encoded data in the fields listed will, by default, be forced to ASCII-8BIT.
# This will, of course, result in a modicum of lost data, but that seems way better than 
# logstash falling over, amirite?

class LogStash::Filters::ForceEncoding < LogStash::Filters::Base

  config_name "force_encoding"

  milestone 1

  # what fields to operate on
  config :fields, :validate => :array, :required => true

  # what charset to use for invalid encodings
  config :to_charset, :validate => :string, :default => 'ASCII-8BIT'

  config :tag, :validate => :string, :default => '_forcedencoding'

  public
  def register
    # nothing to do
  end # def register

  public
  def filter(event)

    # return nothing unless there's an actual filter event
    return unless filter?(event)

    @fields.each do |field|
      next unless event.include?(field)

      unless event[field].valid_encoding?
        event['tags'] ||= []
        event['tags'] |= [@tag]
        event[field].encode!(@to_charset, :invalid => :replace, :undef => :replace, :replace => '').force_encoding(@to_charset)
      end

    end

    # filter_matched should go in the last line of our successful code 
    filter_matched(event)

  end # def filter

end
