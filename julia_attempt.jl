# So far Julia is not as fast but I haven't had time to really optimize. 
# about 40 seconds. 
# 

using Distributed
using Base.Threads

@everywhere begin

function parse_fixed_decimal(s::AbstractVector{UInt8}, start_idx::Int, end_idx::Int)
    val::Int64 = 0
    sign = 1
    for i in start_idx:end_idx
        b = s[i]
        if b == UInt8('-')
            sign = -1
        elseif b != UInt8('.')
            val = val * 10 + (b - UInt8('0'))
        end
    end
    return sign * val / 10.0
end


function read_chunk(start_chunk, end_chunk, filename)
    io = open(filename,"r")
    seek(io,start_chunk)
    s::AbstractVector{UInt8} = read(io,(end_chunk-start_chunk))
    close(io)

    littledict::Dict{String, Vector{Float64}} = Dict()

    sc_indexes = findall(==(UInt8(';')), s)
    prev::Int64 = 1
    for sci::Int64 ∈ sc_indexes
        nxt = findnext(==(UInt8('\n')),s,sci)
        k::String = String(s[prev:sci-1])
        v::Float64 = parse_fixed_decimal(s,sci+1, nxt-1)

        if !haskey(littledict,k)
            littledict[k] = [v,v,v,1.0]
        else
            if v < littledict[k][1]
                littledict[k][1] = v
            end
            if v > littledict[k][2]
                littledict[k][2] = v
            end
            littledict[k][3] += v
            littledict[k][4] += 1
        end
        prev = nxt + 1
    end

    return littledict
end

end # @everywhere


function is_valid_boundary(io_stream::IOStream, pos::Int64)
    if pos == 1
       return true
    end
    seek(io_stream,pos-1)
    return read(io_stream,1,all=false) == b"\n"
end

function get_chunk_bounds(filename)
    fs::Int64 = filesize(filename)
    CPUS::Int64 = 32
    step = round(Int64, fs/CPUS, RoundUp)

    chunk_boundaries = []
    io_stream::IOStream = open(filename)

    chunk_start::Int64 = 1
    for b in 1:31
        chunk_end::Int64 = b*step
        while !is_valid_boundary(io_stream,chunk_end)
            chunk_end -= 1
        end
        push!(chunk_boundaries, (chunk_start, chunk_end))
        chunk_start = chunk_end + 1
    end

    close(io_stream)
    push!(chunk_boundaries, (chunk_start, fs))
    return chunk_boundaries
end


function main()
    bigdict::Dict{String, Vector{Float64}} = Dict()

    fn::String = "data/measurements.csv"

    chunk_boundaries = get_chunk_bounds(fn)

    # Launch all futures first, then fetch — this runs chunks in parallel
    futures = [@spawnat :any read_chunk(start_chunk, end_chunk, fn)
               for (start_chunk, end_chunk) ∈ chunk_boundaries]

    for fut in futures
        littledict = fetch(fut)
        for k in keys(littledict)
            if !haskey(bigdict,k)
                bigdict[k] = littledict[k]
            else
                if littledict[k][1] < bigdict[k][1]
                    bigdict[k][1] = littledict[k][1]
                end
                if littledict[k][2] > bigdict[k][2]
                    bigdict[k][2] = littledict[k][2]
                end
                bigdict[k][3] += littledict[k][3]
                bigdict[k][4] += littledict[k][4]
            end
        end
    end

    for k2 in keys(bigdict)
        println(k2, ";", bigdict[k2][1], '/', bigdict[k2][3]/bigdict[k2][4], '/', bigdict[k2][2])
    end
end


# julia -p 32 julia_attempt.jl

main()
