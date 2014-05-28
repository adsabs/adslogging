
require "logstash/filters/base"
require "logstash/namespace"

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
